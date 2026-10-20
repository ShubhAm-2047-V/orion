"""
Execution Adapter for Approved Machine Commands.
Enforces the strict separation: Interpretation -> Validation -> Authorization -> Execution.
Dispatches authorized, validated commands to Orion Core, EngineRouter, and Win32 subsystems.
"""
import time
from typing import Dict, Any, Optional
from nlu_model.schemas import MachineCommand
from nlu_model.validator import validate_machine_command
from nlu_model.safety import evaluate_command_safety
from engines.permissions import PermissionManager, RiskLevel

class ExecutionResult:
    def __init__(self, success: bool, message: str, data: Any = None, error: Optional[str] = None):
        self.success = success
        self.message = message
        self.data = data or {}
        self.error = error
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp
        }

class OrionExecutionAdapter:
    def __init__(self):
        self.permission_mgr = PermissionManager()

    def execute_command(self, command: MachineCommand, user_confirmed: bool = False) -> ExecutionResult:
        """
        Executes an approved, validated machine command.
        Strictly enforces validation, authorization, and confirmation requirements.
        """
        # Step 1: Validation Check
        val_result = validate_machine_command(command.model_dump())
        if not val_result.is_valid:
            return ExecutionResult(
                success=False,
                message=f"Execution blocked: Validation failed ({'; '.join(val_result.errors)})",
                error="ValidationError"
            )

        # Step 2: Ambiguity Guard
        if command.ambiguity_detected or not command.is_complete:
            return ExecutionResult(
                success=False,
                message=f"Execution blocked: Ambiguous command. {command.clarification_question}",
                error="AmbiguityError"
            )

        # Step 3: Safety & Risk Authorization
        safety = evaluate_command_safety(
            command.raw_input,
            command.intent,
            command.action,
            command.parameters
        )

        if not safety.is_safe:
            return ExecutionResult(
                success=False,
                message=f"Execution blocked by Safety Engine: {safety.reason}",
                error="SecurityViolation"
            )

        if safety.requires_confirmation and not user_confirmed:
            return ExecutionResult(
                success=False,
                message=f"Action '{command.action}' requires explicit confirmation ({safety.reason})",
                data={"requires_confirmation": True, "risk_level": safety.risk_level},
                error="ConfirmationRequired"
            )

        # Step 4: Dispatched Execution via Orion Core & Actions
        try:
            return self._dispatch_to_orion(command)
        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Runtime execution error: {e}",
                error=str(e)
            )

    def _dispatch_to_orion(self, command: MachineCommand) -> ExecutionResult:
        """Dispatches validated intent to Orion system engines."""
        from core import JARVISCore
        core = JARVISCore()
        
        intent = command.intent
        params = command.parameters
        app = params.get("app", "")
        query = params.get("query", "")

        # 1. Open and search
        if intent == "open_application_and_search":
            from actions import open_app, search_web
            open_res = open_app(app or "chrome")
            search_res = search_web(query)
            return ExecutionResult(
                success=True,
                message=f"Launched {app} and opened search for '{query}'.",
                data={"app": app, "query": query, "output": f"{open_res}\n{search_res}"}
            )

        # 2. Open App
        elif intent == "open_application":
            from actions import open_app
            res = open_app(app)
            return ExecutionResult(success=True, message=str(res), data={"app": app})

        # 3. Close App
        elif intent == "close_application":
            from actions import close_app
            res = close_app(app)
            return ExecutionResult(success=True, message=str(res), data={"app": app})

        # 4. Search Web
        elif intent == "search_web":
            from actions import search_web
            res = search_web(query)
            return ExecutionResult(success=True, message=str(res), data={"query": query})

        # 5. Create Folder
        elif intent == "create_folder":
            import os
            from pathlib import Path
            loc = params.get("location", "desktop")
            name = params.get("folder_name", "new_folder")
            target_path = Path.home() / loc.capitalize() / name
            target_path.mkdir(parents=True, exist_ok=True)
            return ExecutionResult(
                success=True,
                message=f"Created folder '{name}' at {target_path}",
                data={"path": str(target_path)}
            )

        # 6. Create File and Code
        elif intent == "create_file_and_code":
            fname = params.get("file_name", "output.txt")
            content = params.get("content", "")
            with open(fname, "w", encoding="utf-8") as f:
                f.write(content + "\n")
            return ExecutionResult(
                success=True,
                message=f"Successfully created file '{fname}' ({len(content)} bytes).",
                data={"file_name": fname}
            )

        # 7. System Diagnostics / Status
        elif intent == "system_status":
            from actions import get_system_status
            res = get_system_status()
            return ExecutionResult(success=True, message=str(res), data={"diagnostics": res})

        # 8. Volume Control
        elif intent == "control_volume":
            from actions import control_volume
            lvl = params.get("level", 50)
            res = control_volume(f"{lvl}")
            return ExecutionResult(success=True, message=f"Volume set to {lvl}%.", data={"level": lvl})

        # 9. Clean Temp
        elif intent == "clean_temp":
            from actions import clean_temp
            res = clean_temp()
            return ExecutionResult(success=True, message=str(res), data={})

        # 10. Lock PC
        elif intent == "lock_pc":
            from actions import lock_pc
            res = lock_pc()
            return ExecutionResult(success=True, message="PC locked.", data={})

        # Generic Router Dispatch
        else:
            cli_input = f"{command.action} {app}".strip()
            res_str = core.process_request(cli_input)
            return ExecutionResult(success=True, message=res_str, data={"output": res_str})
