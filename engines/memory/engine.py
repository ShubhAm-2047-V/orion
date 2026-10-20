"""
Memory Engine for Short-Term Context & Persistent Knowledge.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.shared.memory import MemoryManager

class MemoryEngine(BaseEngine):
    engine_id = "memory"
    name = "Memory Engine"
    description = "Handles JARVIS short-term conversation context, key-value state persistence, and memory clearing."
    capabilities = ["store_memory", "retrieve_memory", "clear_memory"]

    def __init__(self):
        super().__init__()
        self.memory_manager = MemoryManager()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        return any(k in intent_lower for k in ["memory", "remember", "recall", "forget", "clear memory"])

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions: List[Action] = []
        if "clear" in intent or "forget" in intent:
            actions.append(Action("act_1", "clear_memory", self.engine_id))
        elif "remember" in intent or "store" in intent:
            actions.append(Action("act_1", "store_memory", self.engine_id, request))
        else:
            actions.append(Action("act_1", "retrieve_memory", self.engine_id, request))

        return ExecutionPlan("plan_memory", intent, actions, len(actions))

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

            if cap == "store_memory":
                key = params.get("key", "note")
                value = params.get("value", params.get("intent", ""))
                self.memory_manager.set_key(key, value)
                res = f"Stored '{key}': {value}"
            elif cap == "retrieve_memory":
                key = params.get("key", "note")
                res = self.memory_manager.get_key(key, "No memory found.")
            elif cap == "clear_memory":
                self.memory_manager.clear()
                res = "JARVIS memory cleared."
            else:
                res = "Memory action completed."

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_memory", self.engine_id, f"Memory Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
