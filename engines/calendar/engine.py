"""
Calendar Engine for Scheduling, Time, and Alarms.
"""
import time
import re
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.schedule_adapter import ScheduleAdapter

class CalendarEngine(BaseEngine):
    engine_id = "calendar"
    name = "Calendar Engine"
    description = "Handles date/time reports, monthly calendar display, task scheduling, and alarms."
    capabilities = ["get_time", "get_date", "get_calendar", "add_schedule", "list_schedules", "cancel_schedule"]

    def __init__(self):
        super().__init__()
        self.adapter = ScheduleAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        return any(k in intent_lower for k in ["calendar", "time", "date", "schedule", "alarm", "schedules", "cancel schedule"])

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions: List[Action] = []

        if intent in ["time", "date", "what is the time", "what is the date"]:
            actions.append(Action("act_1", "get_time", self.engine_id))
        elif intent == "calendar":
            actions.append(Action("act_1", "get_calendar", self.engine_id))
        elif "list schedules" in intent or intent == "schedules":
            actions.append(Action("act_1", "list_schedules", self.engine_id))
        elif intent.startswith("cancel schedule"):
            m = re.search(r'\d+', intent)
            task_id = int(m.group(0)) if m else 0
            actions.append(Action("act_1", "cancel_schedule", self.engine_id, {"task_id": task_id}))
        else:
            # Parse schedule directive
            actions.append(Action("act_1", "add_schedule", self.engine_id, {"raw_intent": intent}))

        return ExecutionPlan("plan_calendar", intent, actions, len(actions))

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

            if cap in ["get_time", "get_date"]:
                res = self.adapter.get_date_time()
            elif cap == "get_calendar":
                res = self.adapter.get_calendar()
            elif cap == "list_schedules":
                res = self.adapter.list_schedules()
            elif cap == "cancel_schedule":
                res = self.adapter.cancel_schedule(params.get("task_id", 0))
            elif cap == "add_schedule":
                raw = params.get("raw_intent", "")
                # Parse schedule string: "schedule <cmd> in <val>" / "schedule <cmd> at <HH:MM>"
                if " at " in raw:
                    parts = raw.split(" at ", 1)
                    res = self.adapter.add_schedule(parts[0].replace("schedule", "").strip(), "at", parts[1].strip())
                elif " in " in raw:
                    parts = raw.split(" in ", 1)
                    res = self.adapter.add_schedule(parts[0].replace("schedule", "").strip(), "in", parts[1].strip())
                elif " every " in raw:
                    parts = raw.split(" every ", 1)
                    res = self.adapter.add_schedule(parts[0].replace("schedule", "").strip(), "every", parts[1].strip())
                else:
                    res = self.adapter.add_schedule(raw, "in", "10s")
            else:
                res = "Calendar action completed."

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_calendar", self.engine_id, f"Calendar Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
