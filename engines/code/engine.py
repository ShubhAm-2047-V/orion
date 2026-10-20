"""
Code Engine for Developer & Repository Workflows.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.code_adapter import CodeAdapter

class CodeEngine(BaseEngine):
    engine_id = "code"
    name = "Code Engine"
    description = "Handles developer workflows, IDE launch, terminal command execution, and scripts."
    capabilities = ["run_script", "open_ide", "git_workflow", "terminal_exec"]

    def __init__(self):
        super().__init__()
        self.adapter = CodeAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        return any(k in intent_lower for k in ["code", "ide", "git", "terminal", "run command", "script", "antigravity", "vscode"])

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions: List[Action] = []
        if "open" in intent or "ide" in intent:
            actions.append(Action("act_1", "open_ide", self.engine_id, {"ide": "antigravity"}))
        else:
            actions.append(Action("act_1", "terminal_exec", self.engine_id, {"command": intent}))

        return ExecutionPlan("plan_code", intent, actions, len(actions))

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

            if cap == "terminal_exec":
                res = self.adapter.run_shell(params.get("command", ""))
            elif cap == "open_ide":
                res = self.adapter.open_ide(params.get("ide", "antigravity"))
            else:
                res = f"Executed {cap}."

            return ActionResult(True, action.action_id, self.engine_id, str(res), {"output": res}, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_code", self.engine_id, f"Code Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
