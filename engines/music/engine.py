"""
Music & Media Engine.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.media_adapter import MediaAdapter

class MusicEngine(BaseEngine):
    engine_id = "music"
    name = "Music Engine"
    description = "Handles system media playback, volume controls, and track navigation."
    capabilities = ["play_music", "pause_music", "next_track", "prev_track", "set_app_volume"]

    def __init__(self):
        super().__init__()
        self.adapter = MediaAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        import re
        return bool(re.search(r'\b(?:play|pause|skip|next|previous|prev|volume|mute|unmute)\b', intent_lower))

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions: List[Action] = []

        if intent in ["play", "resume"]:
            actions.append(Action("act_1", "play_music", self.engine_id))
        elif intent in ["pause", "stop"]:
            actions.append(Action("act_1", "pause_music", self.engine_id))
        elif intent in ["next", "skip"]:
            actions.append(Action("act_1", "next_track", self.engine_id))
        elif intent in ["previous", "back"]:
            actions.append(Action("act_1", "prev_track", self.engine_id))
        else:
            actions.append(Action("act_1", "set_app_volume", self.engine_id, {"raw": intent}))

        return ExecutionPlan("plan_music", intent, actions, len(actions))

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

            if cap == "play_music":
                res = self.adapter.trigger_media_key("play")
            elif cap == "pause_music":
                res = self.adapter.trigger_media_key("pause")
            elif cap == "next_track":
                res = self.adapter.trigger_media_key("next")
            elif cap == "prev_track":
                res = self.adapter.trigger_media_key("previous")
            elif cap == "set_app_volume":
                raw = params.get("raw", "")
                if "volume status" in raw:
                    res = self.adapter.get_volume_status()
                else:
                    res = self.adapter.control_volume("master", "set", 50)
            else:
                res = "Music action completed."

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_music", self.engine_id, f"Music Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
