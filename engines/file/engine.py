"""
File Engine for Filesystem Operations.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.file_adapter import FileAdapter

class FileEngine(BaseEngine):
    engine_id = "file"
    name = "File Engine"
    description = "Handles local filesystem operations, temp cleanup, recycle bin, file picker, and Explorer."
    capabilities = ["clean_temp", "empty_recycle_bin", "pick_file", "copy_path", "explore_folder"]

    def __init__(self):
        super().__init__()
        self.adapter = FileAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        return any(k in intent_lower for k in ["file", "folder", "temp", "trash", "recycle", "copy path", "explorer"])

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions: List[Action] = []

        if "clean temp" in intent:
            actions.append(Action("act_1", "clean_temp", self.engine_id))
        elif "empty trash" in intent or "recycle bin" in intent:
            actions.append(Action("act_1", "empty_recycle_bin", self.engine_id))
        elif "copy path" in intent:
            target = intent.replace("copy path", "").strip()
            actions.append(Action("act_1", "copy_path", self.engine_id, {"target": target}))
        elif "open file" in intent or "explorer" in intent:
            actions.append(Action("act_1", "explore_folder", self.engine_id))
        else:
            actions.append(Action("act_1", "pick_file", self.engine_id))

        return ExecutionPlan("plan_file", intent, actions, len(actions))

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

            if cap == "clean_temp":
                res = self.adapter.clean_temp()
            elif cap == "empty_recycle_bin":
                res = self.adapter.empty_recycle_bin()
            elif cap == "copy_path":
                res = self.adapter.copy_file_path(params.get("target", ""))
            elif cap == "explore_folder":
                res = self.adapter.open_file_explorer()
            elif cap == "pick_file":
                res = self.adapter.pick_file(params.get("initial_dir"))
            else:
                res = "File action completed."

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_file", self.engine_id, f"File Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
