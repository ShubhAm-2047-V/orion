"""
Multi-Language Machine Code & Structured Command Generator.
Transforms parsed intents & parameters into JSON, Python, JavaScript, SQL, and Shell (PowerShell/Bash).
"""
import json
from typing import Dict, Any
from nlu_model.schemas import GeneratedCode

def generate_multi_language_code(intent: str, engine: str, action: str, params: Dict[str, Any], raw_query: str = "") -> GeneratedCode:
    """
    Generates standardized code representations across JSON, Python, JavaScript, SQL, and Shell.
    """
    # 1. JSON representation
    structured_json = {
        "intent": intent,
        "engine": engine,
        "action": action,
        "parameters": params,
        "confidence": 0.98,
        "target": params.get("app") or params.get("target") or params.get("folder_name") or params.get("file_name") or "system"
    }
    json_str = json.dumps(structured_json, indent=2)

    # 2. Python representation
    py_code = _generate_python_code(intent, engine, action, params)

    # 3. JavaScript representation
    js_code = _generate_javascript_code(intent, engine, action, params)

    # 4. SQL representation
    sql_code = _generate_sql_code(intent, engine, action, params)

    # 5. Shell representation (PowerShell for Windows)
    shell_code = _generate_shell_code(intent, engine, action, params)

    return GeneratedCode(
        json_cmd=json_str,
        python=py_code,
        javascript=js_code,
        sql=sql_code,
        shell=shell_code
    )

def _generate_python_code(intent: str, engine: str, action: str, params: Dict[str, Any]) -> str:
    app = params.get("app", "")
    query = params.get("query", "")
    file_name = params.get("file_name", "")
    folder_name = params.get("folder_name", "")
    location = params.get("location", "desktop")
    content = params.get("content", "")

    if intent == "open_application_and_search":
        return f"""import subprocess, webbrowser
# Launch application and search web query
webbrowser.open("https://www.google.com/search?q={query.replace(' ', '+')}")
subprocess.Popen(["{app}.exe"])
print(f"Launched {app} with query '{query}'")"""

    elif intent == "open_application":
        return f"""import subprocess
# Open application via Windows subprocess
subprocess.Popen(["{app}.exe"])
print(f"Opened {app}")"""

    elif intent == "close_application":
        return f"""import subprocess
# Terminate running process gracefully or forcefully
subprocess.run(["taskkill", "/IM", "{app}.exe", "/F"])
print(f"Terminated {app}")"""

    elif intent == "search_web":
        return f"""import webbrowser
# Open Google search query in default browser
query = "{query}"
webbrowser.open(f"https://www.google.com/search?q={{query}}")
print(f"Searched for: {{query}}")"""

    elif intent == "create_folder":
        return f"""import os
from pathlib import Path

# Resolve path and create directory safely
base_dir = Path.home() / "{location.capitalize()}"
target_folder = base_dir / "{folder_name}"
target_folder.mkdir(parents=True, exist_ok=True)
print(f"Successfully created folder at: {{target_folder}}")"""

    elif intent == "create_file_and_code":
        return f"""# Programmatically generate source file
file_name = "{file_name}"
code_content = \"\"\"{content}\"\"\"

with open(file_name, "w", encoding="utf-8") as f:
    f.write(code_content + "\\n")
print(f"Created file '{{file_name}}' with specified code.")"""

    elif intent == "control_volume":
        lvl = params.get("level", 50)
        return f"""import ctypes
# Set system master volume level ({lvl}%)
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
volume.SetMasterVolumeLevelScalar({lvl / 100.0}, None)
print("Volume updated to {lvl}%")"""

    elif intent == "system_status":
        return """import psutil
# Query CPU, Memory, and Battery telemetry
cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory().percent
battery = psutil.sensors_battery()
print(f"CPU: {cpu}% | RAM: {ram}% | Battery: {battery.percent if battery else 'N/A'}%")"""

    elif intent == "clean_temp":
        return """import os, shutil, tempfile
# Purge temporary files
temp_dir = tempfile.gettempdir()
deleted = 0
for f in os.listdir(temp_dir):
    try:
        p = os.path.join(temp_dir, f)
        if os.path.isfile(p): os.remove(p); deleted += 1
        elif os.path.isdir(p): shutil.rmtree(p); deleted += 1
    except Exception: pass
print(f"Purged {deleted} temporary artifacts.")"""

    elif intent == "whatsapp_message":
        target = params.get("target", "Recipient")
        msg = params.get("message", "Hello")
        return f"""from engines.adapters.whatsapp_adapter import WhatsAppAdapter
# Dispatch automated WhatsApp message
adapter = WhatsAppAdapter()
result = adapter.send_message(target="{target}", message=\"\"\"{msg}\"\"\")
print("WhatsApp delivery status:", result)"""

    else:
        return f"""# Orion Core Dispatched Action
from core import JARVISCore
core = JARVISCore()
result = core.router.route_request("{action} {app}".strip())
print(result)"""

def _generate_javascript_code(intent: str, engine: str, action: str, params: Dict[str, Any]) -> str:
    app = params.get("app", "")
    query = params.get("query", "")
    folder_name = params.get("folder_name", "")
    location = params.get("location", "desktop")

    if intent in ("open_application_and_search", "search_web"):
        return f"""const open = require('open');
// Open query in browser
(async () => {{
  await open(`https://www.google.com/search?q=${{encodeURIComponent('{query}')}}`);
  console.log('Opened browser query: {query}');
}})();"""

    elif intent == "create_folder":
        return f"""const fs = require('fs');
const path = require('path');
const os = require('os');

const targetDir = path.join(os.homedir(), '{location}', '{folder_name}');
fs.mkdirSync(targetDir, {{ recursive: true }});
console.log(`Directory created at: ${{targetDir}}`);"""

    elif intent == "create_file_and_code":
        fname = params.get("file_name", "output.js")
        content = params.get("content", "console.log('Hello World');")
        return f"""const fs = require('fs');
// Write script file
fs.writeFileSync('{fname}', `{content}\\n`, 'utf-8');
console.log('Created file {fname}');"""

    else:
        return f"""// Node.js machine execution payload
const payload = {{
  intent: "{intent}",
  engine: "{engine}",
  action: "{action}",
  params: {json.dumps(params)},
  timestamp: new Date().toISOString()
}};
console.log("Executable Machine Command:", JSON.stringify(payload, null, 2));"""

def _generate_sql_code(intent: str, engine: str, action: str, params: Dict[str, Any]) -> str:
    table = params.get("table", "system_events")
    limit = params.get("limit", 10)
    
    if intent == "database_query":
        return f"""-- Generated Structured Query Language
SELECT *
FROM {table}
ORDER BY created_at DESC
LIMIT {limit};"""

    elif intent in ("system_status", "diagnostics"):
        return """-- Telemetry log persistence
INSERT INTO system_metrics (metric_name, metric_value, recorded_at)
VALUES 
  ('cpu_utilization', 14.5, CURRENT_TIMESTAMP),
  ('ram_utilization', 52.8, CURRENT_TIMESTAMP);"""

    elif intent == "whatsapp_message":
        target = params.get("target", "Contact")
        return f"""-- Audit log for automated communications
INSERT INTO communications_log (channel, recipient, message_preview, status, sent_at)
VALUES ('WhatsApp', '{target}', '{params.get("message", "")[:40]}', 'QUEUED', CURRENT_TIMESTAMP);"""

    else:
        return f"""-- Audit record for {action}
INSERT INTO audit_trail (action_name, engine, parameters_json, executed_at)
VALUES ('{action}', '{engine}', '{json.dumps(params)}', CURRENT_TIMESTAMP);"""

def _generate_shell_code(intent: str, engine: str, action: str, params: Dict[str, Any]) -> str:
    app = params.get("app", "")
    query = params.get("query", "")
    folder_name = params.get("folder_name", "")
    location = params.get("location", "Desktop")

    if intent == "open_application_and_search":
        return f"""# PowerShell execution script
Start-Process "{app}"
Start-Process "https://www.google.com/search?q={query.replace(' ', '+')}"
Write-Host "Launched {app} and opened Google search" -ForegroundColor Green"""

    elif intent == "open_application":
        return f"""# PowerShell launch process
Start-Process "{app}"
Write-Host "Started process: {app}" -ForegroundColor Cyan"""

    elif intent == "close_application":
        return f"""# Terminate application process
Stop-Process -Name "{app}" -Force -ErrorAction SilentlyContinue
Write-Host "Stopped process: {app}" -ForegroundColor Yellow"""

    elif intent == "create_folder":
        return f"""# Create directory in Windows Desktop / Location
$TargetFolder = Join-Path $HOME "{location}\\{folder_name}"
New-Item -ItemType Directory -Path $TargetFolder -Force | Out-Null
Write-Host "Created folder at: $TargetFolder" -ForegroundColor Green"""

    elif intent == "create_file_and_code":
        fname = params.get("file_name", "script.py")
        content = params.get("content", "print('Hello World')")
        return f"""# Create file and write content
@'
{content}
'@ | Set-Content -Path "{fname}" -Encoding UTF8
Write-Host "Created file {fname}" -ForegroundColor Green"""

    elif intent == "clean_temp":
        return """# Purge temp folder
Remove-Item -Path "$env:TEMP\\*" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Temporary artifacts cleared." -ForegroundColor Green"""

    elif intent == "lock_pc":
        return """# Workstation lock
rundll32.exe user32.dll,LockWorkStation
Write-Host "Workstation locked." -ForegroundColor Red"""

    elif intent == "search_web":
        return f"""# Open search query
Start-Process "https://www.google.com/search?q={query.replace(' ', '+')}" """

    else:
        return f"""# Invoke Orion command via CLI
python -c "from core import JARVISCore; print(JARVISCore().process_request('{action} {app}'.Trim()))" """
