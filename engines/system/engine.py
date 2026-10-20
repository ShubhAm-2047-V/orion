"""
System Engine for OS Diagnostics, Power, Memory, and Processes.
"""
import time
import re
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.win32_system_adapter import Win32SystemAdapter
import actions

class SystemEngine(BaseEngine):
    engine_id = "system"
    name = "System Engine"
    description = "Handles OS diagnostics, power management, memory optimization, processes, and themes."
    capabilities = [
        "system_status", "lock_pc", "sleep_pc", "restart_pc", "shutdown_pc",
        "battery_status", "turn_off_screen", "set_theme", "top_processes",
        "idle_time", "disk_check", "optimize_memory", "kill_pid", "keep_awake", "stop_awake", "open_app", "close_app", "schedule_power"
    ]

    def __init__(self):
        super().__init__()
        self.adapter = Win32SystemAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        if any(intent_lower.startswith(prefix) for prefix in ["open ", "launch ", "start ", "run ", "close ", "kill ", "terminate "]):
            return True
        return any(k in intent_lower for k in [
            "status", "diagnostics", "lock pc", "sleep pc", "restart", "shutdown",
            "battery", "screen", "theme", "dark mode", "light mode", "processes",
            "idle", "disk", "storage", "optimize", "kill pid", "awake", "jiggler"
        ])

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions_list: List[Action] = []

        # Check if intent contains delayed or scheduled power/app controls
        rel_sched = re.search(r'\b(?:in|after)\s+(\d+)\s*(s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hr|hrs|hour|hours)\b', intent, re.IGNORECASE)
        abs_sched = re.search(r'\bat\s+(\d{1,2}:\d{2})\b', intent, re.IGNORECASE)
        is_power_cmd = any(k in intent for k in ["shutdown", "turn off", "power off", "restart", "reboot", "sleep"])

        if rel_sched or abs_sched:
            if is_power_cmd:
                if "restart" in intent or "reboot" in intent:
                    cmd_val = "restart pc"
                elif "sleep" in intent:
                    cmd_val = "sleep pc"
                else:
                    cmd_val = "shutdown pc"
            else:
                cmd_val = re.sub(r'\s+(?:in|after)\s+\d+\s*(?:s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hr|hrs|hour|hours)$', '', intent, flags=re.IGNORECASE).strip()
                cmd_val = re.sub(r'\s+at\s+\d{1,2}:\d{2}$', '', cmd_val, flags=re.IGNORECASE).strip()

            if rel_sched:
                val_val = int(rel_sched.group(1))
                unit_val = rel_sched.group(2).lower()
                multiplier = 1
                if unit_val.startswith("m"):
                    multiplier = 60
                elif unit_val.startswith("h"):
                    multiplier = 3600
                trigger_time = time.time() + (val_val * multiplier)
                actions_list.append(Action("act_1", "schedule_power", self.engine_id, {
                    "task_type": "one-shot", "trigger_val": trigger_time, "command": cmd_val
                }))
            elif abs_sched:
                import datetime
                time_val = abs_sched.group(1)
                if len(time_val.split(":")[0]) == 1:
                    time_val = "0" + time_val
                now_dt = datetime.datetime.now()
                target_dt_str = f"{now_dt.strftime('%Y-%m-%d')} {time_val}:00"
                target_dt = datetime.datetime.strptime(target_dt_str, "%Y-%m-%d %H:%M:%S")
                if now_dt > target_dt:
                    target_dt += datetime.timedelta(days=1)
                    target_dt_str = target_dt.strftime("%Y-%m-%d %H:%M:%S")
                actions_list.append(Action("act_1", "schedule_power", self.engine_id, {
                    "task_type": "one-shot", "trigger_val": target_dt_str, "command": cmd_val
                }))
        elif any(intent.startswith(prefix) for prefix in ["close ", "kill ", "terminate "]):
            actions_list.append(Action("act_1", "close_app", self.engine_id, {"app": intent}))
        elif any(intent.startswith(prefix) for prefix in ["open ", "launch ", "start ", "run "]):
            actions_list.append(Action("act_1", "open_app", self.engine_id, {"app": intent}))
        elif intent in ["status", "diagnostics", "system status"]:
            actions_list.append(Action("act_1", "system_status", self.engine_id))
        elif "lock" in intent:
            actions_list.append(Action("act_1", "lock_pc", self.engine_id))
        elif "sleep pc" in intent:
            actions_list.append(Action("act_1", "sleep_pc", self.engine_id))
        elif "restart" in intent or "reboot" in intent:
            actions_list.append(Action("act_1", "restart_pc", self.engine_id))
        elif "shutdown" in intent:
            actions_list.append(Action("act_1", "shutdown_pc", self.engine_id))
        elif "battery" in intent:
            actions_list.append(Action("act_1", "battery_status", self.engine_id))
        elif "turn off screen" in intent:
            actions_list.append(Action("act_1", "turn_off_screen", self.engine_id))
        elif "dark mode" in intent or "light mode" in intent:
            mode = "dark" if "dark" in intent else "light"
            actions_list.append(Action("act_1", "set_theme", self.engine_id, {"theme": mode}))
        elif "top processes" in intent or "processes" in intent:
            actions_list.append(Action("act_1", "top_processes", self.engine_id))
        elif "idle" in intent:
            actions_list.append(Action("act_1", "idle_time", self.engine_id))
        elif "disk" in intent or "storage" in intent:
            actions_list.append(Action("act_1", "disk_check", self.engine_id))
        elif "optimize" in intent:
            actions_list.append(Action("act_1", "optimize_memory", self.engine_id))
        elif "kill pid" in intent:
            m = re.search(r'\d+', intent)
            pid = int(m.group(0)) if m else 0
            actions_list.append(Action("act_1", "kill_pid", self.engine_id, {"pid": pid}))
        elif "stop awake" in intent or "disable awake" in intent or "deactivate awake" in intent:
            actions_list.append(Action("act_1", "stop_awake", self.engine_id))
        elif "awake" in intent or "jiggler" in intent:
            actions_list.append(Action("act_1", "keep_awake", self.engine_id))
        else:
            actions_list.append(Action("act_1", "system_status", self.engine_id))

        return ExecutionPlan("plan_system", intent, actions_list, len(actions_list))

    def validate(self, action: Action) -> ValidationResult:
        if action.capability not in self.capabilities:
            return ValidationResult(False, f"Unsupported capability '{action.capability}'")
        return ValidationResult(True)

    def execute(self, action: Action) -> ActionResult:
        start_time = time.time()
        try:
            val_res = self.validate(action)
            if not val_res.is_valid:
                return ActionResult(False, action.action_id, self.engine_id, val_res.reason or "Validation failed")

            cap = action.capability
            params = action.parameters

            if cap == "system_status":
                res = self.adapter.get_status()
            elif cap == "lock_pc":
                res = self.adapter.lock_pc()
            elif cap == "sleep_pc":
                res = self.adapter.set_power_state("sleep")
            elif cap == "restart_pc":
                res = self.adapter.set_power_state("restart")
            elif cap == "shutdown_pc":
                res = self.adapter.set_power_state("shutdown")
            elif cap == "schedule_power":
                res = actions.add_jarvis_schedule(
                    params.get("task_type", "one-shot"),
                    params.get("trigger_val"),
                    params.get("command", "shutdown pc")
                )
            elif cap == "battery_status":
                res = actions.get_battery_status()
            elif cap == "turn_off_screen":
                res = self.adapter.turn_off_screen()
            elif cap == "set_theme":
                res = self.adapter.set_system_theme(params.get("theme", "dark"))
            elif cap == "top_processes":
                res = self.adapter.get_top_processes()
            elif cap == "idle_time":
                res = self.adapter.get_idle_time()
            elif cap == "disk_check":
                res = self.adapter.get_disk_breakdown()
            elif cap == "optimize_memory":
                res = self.adapter.optimize_memory()
            elif cap == "kill_pid":
                res = self.adapter.kill_pid(params.get("pid", 0))
            elif cap == "keep_awake":
                res = self.adapter.start_keep_awake()
            elif cap == "stop_awake":
                res = self.adapter.stop_keep_awake()
            elif cap == "open_app":
                res = actions.open_app(params.get("app", ""))
            elif cap == "close_app":
                res = actions.close_app(params.get("app", ""))
            else:
                res = "System action completed."

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_system", self.engine_id, f"System Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
