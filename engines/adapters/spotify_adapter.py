"""
Spotify App Adapter for JARVIS.
"""
from typing import Dict, Any
from engines.adapters.base import BaseAdapter
import actions

class SpotifyAdapter(BaseAdapter):
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok"}

    def play(self) -> str:
        return actions.trigger_media_key("play")

    def pause(self) -> str:
        return actions.trigger_media_key("pause")

    def next_track(self) -> str:
        return actions.trigger_media_key("next")

    def previous_track(self) -> str:
        return actions.trigger_media_key("previous")

    def open_app(self) -> str:
        return actions.open_app("spotify")
