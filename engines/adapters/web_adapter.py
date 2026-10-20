"""
Web & Search Adapter for JARVIS.
"""
from typing import Dict, Any
from engines.adapters.base import BaseAdapter
import actions

class WebAdapter(BaseAdapter):
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok"}

    def search_web(self, query: str) -> str:
        return actions.search_web(query)

    def open_url(self, url: str) -> str:
        return actions.open_url(url)

    def open_youtube(self) -> str:
        return actions.trigger_youtube_hotkey()
