"""
WhatsApp Specialized App Engine.
"""
import time
import re
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.whatsapp_adapter import WhatsAppAdapter
import actions

class WhatsAppEngine(BaseEngine):
    engine_id = "whatsapp"
    name = "WhatsApp Engine"
    description = "Handles all WhatsApp Web automations including login, text messages, media files, unreads, calls, status checks, broadcasting, and auto-reply."
    capabilities = [
        "whatsapp_login", "whatsapp_send_msg", "whatsapp_send_file",
        "whatsapp_unreads", "whatsapp_status", "whatsapp_call",
        "whatsapp_broadcast", "whatsapp_auto_reply", "whatsapp_mute", "whatsapp_logout", "schedule_action"
    ]

    def __init__(self):
        super().__init__()
        self.adapter = WhatsAppAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        return intent_lower.startswith("whatsapp") or " whatsapp" in intent_lower or intent_lower.startswith("wa ")

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").strip()
        intent_lower = intent.lower()
        actions_list: List[Action] = []

        # Check for timing / schedule clauses in request
        rel_sched = re.search(r'\b(?:in|after)\s+(\d+)\s*(s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hr|hrs|hour|hours)\b', intent_lower)
        abs_sched = re.search(r'\bat\s+(\d{1,2}:\d{2})\b', intent_lower)

        if rel_sched or abs_sched:
            if rel_sched:
                val_val = int(rel_sched.group(1))
                unit_val = rel_sched.group(2).lower()
                multiplier = 1
                if unit_val.startswith("m"):
                    multiplier = 60
                elif unit_val.startswith("h"):
                    multiplier = 3600
                trigger_time = time.time() + (val_val * multiplier)
                clean_cmd = re.sub(r'\s+(?:in|after)\s+\d+\s*(?:s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hr|hrs|hour|hours)$', '', intent, flags=re.IGNORECASE).strip()
                actions_list.append(Action("act_1", "schedule_action", self.engine_id, {
                    "task_type": "one-shot", "trigger_val": trigger_time, "command": clean_cmd
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
                clean_cmd = re.sub(r'\s+at\s+\d{1,2}:\d{2}$', '', intent, flags=re.IGNORECASE).strip()
                actions_list.append(Action("act_1", "schedule_action", self.engine_id, {
                    "task_type": "one-shot", "trigger_val": target_dt_str, "command": clean_cmd
                }))
            return ExecutionPlan("plan_whatsapp", intent, actions_list, len(actions_list))

        if any(kw in intent_lower for kw in ["whatsapp login", "open whatsapp", "launch whatsapp", "start whatsapp", "whatsapp open", "open wa", "kholo whatsapp", "chalu whatsapp"]):
            actions_list.append(Action("act_1", "whatsapp_login", self.engine_id))
        elif "whatsapp logout" in intent_lower:
            actions_list.append(Action("act_1", "whatsapp_logout", self.engine_id))
        elif "whatsapp unreads" in intent_lower:
            actions_list.append(Action("act_1", "whatsapp_unreads", self.engine_id))
        elif "whatsapp send file" in intent_lower or "send file" in intent_lower:
            actions_list.append(Action("act_1", "whatsapp_send_file", self.engine_id, {"raw": intent}))
        elif "call" in intent_lower:
            actions_list.append(Action("act_1", "whatsapp_call", self.engine_id, {"raw": intent}))
        elif "broadcast" in intent_lower:
            actions_list.append(Action("act_1", "whatsapp_broadcast", self.engine_id, {"raw": intent}))
        elif "status" in intent_lower:
            actions_list.append(Action("act_1", "whatsapp_status", self.engine_id, {"raw": intent}))
        elif "auto-reply" in intent_lower or "autoreply" in intent_lower:
            actions_list.append(Action("act_1", "whatsapp_auto_reply", self.engine_id, {"raw": intent}))
        elif "mute" in intent_lower:
            actions_list.append(Action("act_1", "whatsapp_mute", self.engine_id, {"raw": intent}))
        else:
            actions_list.append(Action("act_1", "whatsapp_send_msg", self.engine_id, {"raw": intent}))

        return ExecutionPlan("plan_whatsapp", intent, actions_list, len(actions_list))

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

            if cap == "schedule_action":
                res = actions.add_jarvis_schedule(
                    params.get("task_type", "one-shot"),
                    params.get("trigger_val"),
                    params.get("command")
                )

            if cap == "whatsapp_login":
                opened = actions.open_app("whatsapp")
                if opened:
                    return ActionResult(True, action.action_id, self.engine_id, "Successfully opened WhatsApp application.")
                res = self.adapter.login()
            elif cap == "whatsapp_logout":
                res = self.adapter.logout()
            elif cap == "whatsapp_unreads":
                res = self.adapter.get_unreads()
            elif cap == "whatsapp_send_msg":
                raw = params.get("raw", "")
                target = params.get("target")
                text = params.get("text")
                if not target or not text:
                    # Parse from raw: "whatsapp message to <target> text <text>"
                    match = re.search(r'to\s+(.*?)\s+text\s+(.*)', raw, re.IGNORECASE)
                    if match:
                        target = match.group(1).strip()
                        text = match.group(2).strip()
                    else:
                        target = "Contact"
                        text = raw
                res = self.adapter.send_message(target, text)
            elif cap == "whatsapp_send_file":
                raw = params.get("raw", "")
                target = params.get("target")
                file_path = params.get("file_path")
                if not target:
                    match = re.search(r'to\s+([^\s]+)', raw, re.IGNORECASE)
                    target = match.group(1).strip() if match else "Contact"
                res = self.adapter.send_file(target, file_path)
            elif cap == "whatsapp_call":
                raw = params.get("raw", "")
                target = params.get("target", "Contact")
                call_type = "video" if "video" in raw.lower() else "voice"
                res = self.adapter.trigger_call(target, call_type)
            elif cap == "whatsapp_status":
                raw = params.get("raw", "")
                match = re.search(r'of\s+([^\s]+)', raw, re.IGNORECASE)
                target = match.group(1).strip() if match else "Contact"
                res = self.adapter.get_status(target)
            elif cap == "whatsapp_broadcast":
                raw = params.get("raw", "")
                res = f"Broadcasting message: {raw}"
            elif cap == "whatsapp_auto_reply":
                res = self.adapter.auto_reply("on", "Auto reply message")
            elif cap == "whatsapp_mute":
                raw = params.get("raw", "")
                res = self.adapter.mute_chat(raw)
            else:
                res = "WhatsApp action completed."

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_whatsapp", self.engine_id, f"WhatsApp Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
