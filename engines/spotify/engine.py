"""
Spotify Specialized App Engine.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.spotify_adapter import SpotifyAdapter

class SpotifyEngine(BaseEngine):
    engine_id = "spotify"
    name = "Spotify Engine"
    description = "Handles Spotify app playback controls and track search."
    capabilities = ["play_spotify", "pause_spotify", "search_spotify"]

    def __init__(self):
        super().__init__()
        self.adapter = SpotifyAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return "spotify" in intent.lower()

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions: List[Action] = []
        if "pause" in intent:
            actions.append(Action("act_1", "pause_spotify", self.engine_id))
        elif "search" in intent:
            actions.append(Action("act_1", "search_spotify", self.engine_id, request))
        else:
            actions.append(Action("act_1", "play_spotify", self.engine_id))

        return ExecutionPlan("plan_spotify", intent, actions, len(actions))

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
            if cap == "pause_spotify":
                res = self.adapter.pause()
            else:
                res = self.adapter.play()

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_spotify", self.engine_id, f"Spotify Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
