"""
File System Adapter for JARVIS FileEngine.
"""
from typing import Dict, Any, Optional
from engines.adapters.base import BaseAdapter
import actions

class FileAdapter(BaseAdapter):
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok"}

    def clean_temp(self) -> str:
        return actions.clean_temp()

    def empty_recycle_bin(self) -> str:
        return actions.empty_recycle_bin()

    def take_screenshot(self) -> str:
        return actions.take_screenshot()

    def copy_file_path(self, target: str) -> str:
        return actions.copy_file_path(target)

    def clear_clipboard(self) -> str:
        return actions.clear_clipboard()

    def pick_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        return actions.select_file_via_picker(initial_dir)

    def open_file_explorer(self) -> str:
        return actions.trigger_file_explorer_hotkey()
