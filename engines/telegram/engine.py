"""
Telegram Engine for Telegram Automation.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.telegram_adapter import TelegramAdapter

class TelegramEngine(BaseEngine):
    engine_id = "telegram"
    name = "Telegram Engine"
    description = "Handles Telegram messaging and automation workflows."
    capabilities = ["telegram_send_msg", "telegram_read_msg"]

    def __init__(self):
        super().__init__()
        self.adapter = TelegramAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return "telegram" in intent.lower()

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "")
        actions = [Action("act_1", "telegram_send_msg", self.engine_id, request)]
        return ExecutionPlan("plan_telegram", intent, actions, 1)

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

            recipient = action.parameters.get("recipient", "User")
            message = action.parameters.get("message", action.parameters.get("intent", ""))
            res = self.adapter.send_message(recipient, message)
            return ActionResult(True, action.action_id, self.engine_id, res, {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_telegram", self.engine_id, f"Telegram Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
