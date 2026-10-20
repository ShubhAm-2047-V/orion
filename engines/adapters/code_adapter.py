"""
Code & Development Workflow Adapter for JARVIS.
"""
from typing import Dict, Any
from engines.adapters.base import BaseAdapter
import actions

class CodeAdapter(BaseAdapter):
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok"}

    def run_shell(self, command: str) -> str:
        return actions.run_shell_command(command)

    def open_ide(self, ide_name: str = "antigravity") -> str:
        return actions.open_app(ide_name)
