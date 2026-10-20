"""
JARVIS Control Center & Engine Configurator HTTP Dashboard Server.
Provides REST API endpoints for configuring engines, core settings, security permissions, and executing test prompts.
"""
import os
import sys
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Ensure workspace root is in sys.path
workspace_root = os.path.dirname(os.path.abspath(__file__))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from core import JARVISCore
from engines.shared.config import ConfigManager
from engines.permissions import PermissionManager, RiskLevel

PORT = 8000
core_instance = None

def get_core():
    global core_instance
    if core_instance is None:
        core_instance = JARVISCore()
    return core_instance

class JARVISDashboardHandler(BaseHTTPRequestHandler):
    def _set_json_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _set_file_headers(self, content_type, status=200):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()

    def do_OPTIONS(self):
        self._set_json_headers(200)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            core = get_core()
            reg = core.registry
            perm = core.permissions
            
            data = {
                "status": "online",
                "active_engines": len(reg.list()),
                "total_capabilities": sum(len(e.capabilities) for e in reg.list()),
                "uptime_seconds": round(time.time() - getattr(core, "_start_time", time.time()), 2),
                "system_info": core.router.route_request("system status")[0].data if reg.get("system") else {}
            }
            self._set_json_headers(200)
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        elif path == "/api/engines":
            core = get_core()
            reg = core.registry
            perm = core.permissions
            
            engines_list = []
            for engine in reg.list():
                cap_details = []
                for cap in engine.capabilities:
                    cap_details.append({
                        "name": cap,
                        "risk_level": perm.get_risk_level(cap).name
                    })

                engines_list.append({
                    "engine_id": engine.engine_id,
                    "name": engine.name,
                    "description": engine.description,
                    "initialized": engine.initialized,
                    "capabilities": cap_details,
                    "health": engine.health_check()
                })

            self._set_json_headers(200)
            self.wfile.write(json.dumps(engines_list).encode('utf-8'))
            return

        elif path == "/api/core/config":
            cfg = ConfigManager()
            self._set_json_headers(200)
            self.wfile.write(json.dumps(cfg.data).encode('utf-8'))
            return

        elif path == "/api/telemetry":
            core = get_core()
            recent_history = core.memory.get_recent_history(20)
            self._set_json_headers(200)
            self.wfile.write(json.dumps(recent_history).encode('utf-8'))
            return

        # Serve static dashboard files
        dashboard_dir = os.path.join(workspace_root, "dashboard")
        file_map = {
            "/": "index.html",
            "/index.html": "index.html",
            "/styles.css": "styles.css",
            "/app.js": "app.js"
        }
        
        target_filename = file_map.get(path, path.lstrip("/"))
        file_path = os.path.join(dashboard_dir, target_filename)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            content_types = {
                ".html": "text/html",
                ".css": "text/css",
                ".js": "application/javascript",
                ".json": "application/json",
                ".png": "image/png",
                ".svg": "image/svg+xml"
            }
            c_type = content_types.get(ext, "text/plain")
            self._set_file_headers(c_type, 200)
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self._set_json_headers(404)
            self.wfile.write(json.dumps({"error": "File not found"}).encode('utf-8'))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            body = json.loads(post_data)
        except Exception:
            body = {}

        if path == "/api/execute":
            prompt = body.get("prompt", "")
            core = get_core()
            start_t = time.time()
            output = core.process_request(prompt)
            duration = round(time.time() - start_t, 3)

            resp = {
                "prompt": prompt,
                "output": output,
                "execution_time_seconds": duration
            }
            self._set_json_headers(200)
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        elif path == "/api/engines/config":
            # Update capability risk level or engine settings
            capability = body.get("capability")
            risk_name = body.get("risk_level", "NORMAL")
            
            perm = get_core().permissions
            if capability and hasattr(RiskLevel, risk_name):
                perm.register_risk_level(capability, getattr(RiskLevel, risk_name))
                resp = {"status": "updated", "capability": capability, "risk_level": risk_name}
                self._set_json_headers(200)
            else:
                resp = {"error": "Invalid capability or risk level"}
                self._set_json_headers(400)

            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        elif path == "/api/core/config":
            cfg = ConfigManager()
            if "applications" in body:
                cfg.set("applications", body["applications"])
            if "voice" in body:
                cfg.set("voice", body["voice"])
            if "macros" in body:
                cfg.set("macros", body["macros"])
            
            resp = {"status": "success", "config": cfg.data}
            self._set_json_headers(200)
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        elif path == "/api/engines/health":
            core = get_core()
            health_map = core.registry.health_check_all()
            self._set_json_headers(200)
            self.wfile.write(json.dumps(health_map).encode('utf-8'))
            return

        # --- NLU AI Model Endpoints ---
        elif path == "/api/nlu/interpret":
            from nlu_model.engine import NLUEngine
            from nlu_model.validator import validate_machine_command
            query = body.get("query", "")
            nlu = NLUEngine()
            cmd = nlu.understand(query)
            cmd_dict = cmd.model_dump()
            val_result = validate_machine_command(cmd_dict)
            
            resp = {
                "command": cmd_dict,
                "validation": val_result.to_dict()
            }
            self._set_json_headers(200)
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        elif path == "/api/nlu/execute":
            from nlu_model.schemas import MachineCommand
            from nlu_model.execution_adapter import OrionExecutionAdapter
            raw_cmd = body.get("command", {})
            user_confirmed = body.get("confirmed", False)
            try:
                cmd_obj = MachineCommand(**raw_cmd)
                adapter = OrionExecutionAdapter()
                exec_res = adapter.execute_command(cmd_obj, user_confirmed=user_confirmed)
                resp = exec_res.to_dict()
                self._set_json_headers(200)
            except Exception as e:
                resp = {"success": False, "message": f"Execution error: {e}", "error": str(e)}
                self._set_json_headers(400)
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        elif path == "/api/nlu/voice-listen":
            from nlu_model.voice_processor import VoiceProcessor
            lang = body.get("language", "en")
            timeout = body.get("timeout", 5)
            vp = VoiceProcessor()
            voice_res = vp.listen(language_key=lang, timeout=timeout)
            self._set_json_headers(200)
            self.wfile.write(json.dumps(voice_res.to_dict()).encode('utf-8'))
            return

        elif path == "/api/nlu/train":
            from nlu_model.trainer import train_orion_model
            from nlu_model.engine import NLUEngine
            meta = train_orion_model()
            NLUEngine()._load_model()
            self._set_json_headers(200)
            self.wfile.write(json.dumps({"status": "success", "metadata": meta}).encode('utf-8'))
            return

        self._set_json_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

def run_server(port=PORT):
    server_address = ('', port)
    httpd = HTTPServer(server_address, JARVISDashboardHandler)
    print(f"[JARVIS Dashboard]: Server active at http://localhost:{port}")
    httpd.serve_forever()

def start_dashboard_in_background(port=PORT):
    t = threading.Thread(target=run_server, args=(port,), daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    run_server(PORT)
