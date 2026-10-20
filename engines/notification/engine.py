"""
Notification Engine for System Notifications, Alerts, and Alarms.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.voice_adapter import VoiceAdapter

class NotificationEngine(BaseEngine):
    engine_id = "notification"
    name = "Notification Engine"
    description = "Handles desktop notifications, speech alerts, and audio alarms."
    capabilities = ["send_notification", "alert_user", "play_alarm_sound"]

    def __init__(self):
        super().__init__()
        self.adapter = VoiceAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        return any(k in intent_lower for k in ["notify", "notification", "alert", "alarm message"])

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "")
        actions = [Action("act_1", "alert_user", self.engine_id, {"message": intent})]
        return ExecutionPlan("plan_notification", intent, actions, 1)

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

            msg = action.parameters.get("message", "Alert notification")
            self.adapter.speak(msg)
            res = f"Notification delivered: {msg}"

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_notification", self.engine_id, f"Notification Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
