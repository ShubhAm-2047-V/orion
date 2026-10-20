"""
Schedule & Calendar Adapter for JARVIS.
"""
from typing import Dict, Any
from engines.adapters.base import BaseAdapter
import actions

class ScheduleAdapter(BaseAdapter):
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok"}

    def add_schedule(self, target_cmd: str, timing_type: str, timing_val: str) -> str:
        return actions.add_jarvis_schedule(target_cmd, timing_type, timing_val)

    def list_schedules(self) -> str:
        return actions.list_jarvis_schedules()

    def cancel_schedule(self, task_id: int) -> str:
        return actions.cancel_jarvis_schedule(task_id)

    def get_date_time(self) -> str:
        return actions.get_date_time()

    def get_calendar(self) -> str:
        return actions.get_calendar()
