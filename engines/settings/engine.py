"""
Settings Engine for Windows Settings Deep Links.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.win32_system_adapter import Win32SystemAdapter

class SettingsEngine(BaseEngine):
    engine_id = "settings"
    name = "Settings Engine"
    description = "Handles system configuration deep links (WiFi, Bluetooth, Display, Sound, Update)."
    capabilities = ["open_settings", "toggle_wifi_settings", "toggle_bluetooth_settings", "toggle_display_settings", "close_settings"]

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
        return "settings" in intent_lower or any(k in intent_lower for k in ["wifi settings", "bluetooth settings", "display settings", "sound settings", "update settings", "open wifi", "open bluetooth", "open display", "open sound", "open update"])

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions_list: List[Action] = []
        
        if any(kw in intent for kw in ["close", "terminate", "kill", "shut"]):
            actions_list.append(Action("act_1", "close_settings", self.engine_id))
        else:
            page = "settings"
            for candidate in ["wifi", "bluetooth", "display", "sound", "update"]:
                if candidate in intent:
                    page = candidate
                    break
            actions_list.append(Action("act_1", "open_settings", self.engine_id, {"page": page}))

        return ExecutionPlan("plan_settings", intent, actions_list, len(actions_list))

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
            if cap == "close_settings":
                import actions
                res = actions.close_app("settings")
            else:
                page = action.parameters.get("page", "settings")
                res = self.adapter.open_settings_page(page)

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_settings", self.engine_id, f"Settings Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
