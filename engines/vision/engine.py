"""
Vision Engine for Screenshots and Visual Operations.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.file_adapter import FileAdapter

class VisionEngine(BaseEngine):
    engine_id = "vision"
    name = "Vision Engine"
    description = "Handles desktop screenshots and image analysis."
    capabilities = ["take_screenshot", "analyze_image"]

    def __init__(self):
        super().__init__()
        self.adapter = FileAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        return any(k in intent_lower for k in ["screenshot", "capture", "screen", "image", "vision"])

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions = [Action("act_1", "take_screenshot", self.engine_id)]
        return ExecutionPlan("plan_vision", intent, actions, 1)

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

            res = self.adapter.take_screenshot()
            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_vision", self.engine_id, f"Vision Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
