"""
YouTube Engine for YouTube Operations.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.web_adapter import WebAdapter

class YouTubeEngine(BaseEngine):
    engine_id = "youtube"
    name = "YouTube Engine"
    description = "Handles YouTube website launching, searching, and video operations."
    capabilities = ["launch_youtube", "search_youtube", "play_video"]

    def __init__(self):
        super().__init__()
        self.adapter = WebAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return "youtube" in intent.lower() or "yt" in intent.lower()

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions: List[Action] = []
        if "search" in intent:
            query = intent.replace("search youtube", "").replace("youtube search", "").strip()
            actions.append(Action("act_1", "search_youtube", self.engine_id, {"query": query}))
        else:
            actions.append(Action("act_1", "launch_youtube", self.engine_id))

        return ExecutionPlan("plan_youtube", intent, actions, len(actions))

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
            if cap == "search_youtube":
                q = action.parameters.get("query", "")
                res = self.adapter.open_url(f"https://www.youtube.com/results?search_query={q}")
            else:
                res = self.adapter.open_youtube()

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_youtube", self.engine_id, f"YouTube Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
