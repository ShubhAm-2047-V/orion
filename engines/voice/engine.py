"""
Voice Engine for Speech Recognition & Voice Synthesis.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.voice_adapter import VoiceAdapter
from engines.adapters.media_adapter import MediaAdapter

class VoiceEngine(BaseEngine):
    engine_id = "voice"
    name = "Voice Engine"
    description = "Handles speech recognition, hands-free voice loop mode, TTS output, and microphone muting."
    capabilities = ["listen_voice", "voice_loop", "speak_text", "mute_microphone", "unmute_microphone"]

    def __init__(self):
        super().__init__()
        self.adapter = VoiceAdapter()
        self.media_adapter = MediaAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return self.adapter.health_check()

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        return any(k in intent_lower for k in ["voice", "listen", "speak", "microphone", "mic"])

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions: List[Action] = []

        if "loop" in intent or "mode" in intent:
            actions.append(Action("act_1", "voice_loop", self.engine_id))
        elif "mute mic" in intent or "microphone" in intent:
            action_type = "unmute" if "unmute" in intent else "mute"
            cap = "unmute_microphone" if action_type == "unmute" else "mute_microphone"
            actions.append(Action("act_1", cap, self.engine_id))
        elif "speak" in intent:
            text = intent.replace("speak", "").strip()
            actions.append(Action("act_1", "speak_text", self.engine_id, {"text": text}))
        else:
            actions.append(Action("act_1", "listen_voice", self.engine_id))

        return ExecutionPlan("plan_voice", intent, actions, len(actions))

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

            if cap == "listen_voice":
                res = self.adapter.listen()
            elif cap == "voice_loop":
                self.adapter.start_voice_loop()
                res = "Voice loop activated."
            elif cap == "speak_text":
                self.adapter.speak(params.get("text", ""))
                res = "Spoke text."
            elif cap == "mute_microphone":
                res = self.media_adapter.control_microphone("mute")
            elif cap == "unmute_microphone":
                res = self.media_adapter.control_microphone("unmute")
            else:
                res = "Voice action completed."

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_voice", self.engine_id, f"Voice Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
