"""
Search Engine for Web & Information Lookup.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.web_adapter import WebAdapter

class SearchEngine(BaseEngine):
    engine_id = "search"
    name = "Search Engine"
    description = "Handles Google queries and web information lookup."
    capabilities = ["web_search_query", "info_lookup"]

    def __init__(self):
        super().__init__()
        self.adapter = WebAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        return intent_lower.startswith("search ") or "google" in intent_lower or "lookup" in intent_lower

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").strip()
        query = intent.replace("search", "").replace("google", "").strip()
        actions = [Action("act_1", "web_search_query", self.engine_id, {"query": query})]
        return ExecutionPlan("plan_search", intent, actions, 1)

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

            q = action.parameters.get("query", "")
            res = self.adapter.search_web(q)
            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_search", self.engine_id, f"Search Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
