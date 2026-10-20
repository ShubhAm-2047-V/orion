"""
Voice Subsystem Adapter for JARVIS.
"""
from typing import Dict, Any, Optional
from engines.adapters.base import BaseAdapter
import voice_engine
import actions

class VoiceAdapter(BaseAdapter):
    def health_check(self) -> Dict[str, Any]:
        rec, mic, err = voice_engine.get_speech_recognizer_and_mic()
        return {
            "status": "ok" if not err else "degraded",
            "error": err
        }

    def listen(self, timeout: int = 5, phrase_limit: int = 5) -> Optional[str]:
        return voice_engine.listen_for_command(timeout=timeout, phrase_time_limit=phrase_limit)

    def start_voice_loop(self) -> None:
        voice_engine.voice_loop_mode()

    def speak(self, text: str, force: bool = False) -> None:
        actions.speak(text, print_to_console=False)
