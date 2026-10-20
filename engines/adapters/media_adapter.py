"""
Media & Audio Hardware Adapter for JARVIS.
"""
from typing import Dict, Any
from engines.adapters.base import BaseAdapter
import actions

class MediaAdapter(BaseAdapter):
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok"}

    def control_volume(self, target: str, action_type: str, level: int = 50) -> str:
        return actions.control_volume(target, action_type, level)

    def get_volume_status(self) -> str:
        return actions.get_volume_status()

    def trigger_media_key(self, key_action: str) -> str:
        return actions.trigger_media_key(key_action)

    def control_microphone(self, action_type: str) -> str:
        return actions.control_microphone(action_type)
