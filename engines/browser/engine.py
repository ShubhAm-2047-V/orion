"""
Browser Engine for Web Browsing Operations.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.web_adapter import WebAdapter
from engines.shared.errors import EngineInitializationError

class BrowserEngine(BaseEngine):
    engine_id = "browser"
    name = "Browser Engine"
    description = "Handles web browser navigation, direct URL launching, and web search."
    capabilities = ["open_url", "web_search", "open_website", "close_browser"]

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
        return any(cap in intent_lower for cap in ["url", "website", "http", "www", "chrome", "edge"]) or "search" in intent_lower

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").strip()
        intent_lower = intent.lower()

        actions: List[Action] = []
        if intent_lower.startswith("website ") or "open_website" in request:
            url = intent[8:].strip() if intent_lower.startswith("website ") else request.get("url", "")
            actions.append(Action("action_1", "open_website", self.engine_id, {"url": url}))
        elif intent_lower.startswith("search ") or "web_search" in request:
            query = intent[7:].strip() if intent_lower.startswith("search ") else request.get("query", "")
            actions.append(Action("action_1", "web_search", self.engine_id, {"query": query}))
        else:
            actions.append(Action("action_1", "open_url", self.engine_id, {"url": request.get("url", intent)}))

        return ExecutionPlan("plan_browser", intent, actions, len(actions))

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

            if cap in ["open_url", "open_website"]:
                url = params.get("url", "")
                res = self.adapter.open_url(url)
            elif cap == "web_search":
                query = params.get("query", "")
                res = self.adapter.search_web(query)
            else:
                res = f"Action '{cap}' executed."

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_browser", self.engine_id, f"Browser Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
