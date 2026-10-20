"""
Email Engine for Email Operations.
"""
import time
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan
from engines.adapters.email_adapter import EmailAdapter

class EmailEngine(BaseEngine):
    engine_id = "email"
    name = "Email Engine"
    description = "Handles sending emails, reading emails, and downloading attachments."
    capabilities = ["send_email", "read_emails", "fetch_attachments"]

    def __init__(self):
        super().__init__()
        self.adapter = EmailAdapter()

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self.initialized}

    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        intent_lower = intent.lower()
        return any(k in intent_lower for k in ["email", "mail", "gmail", "outlook", "inbox", "attachment"])

    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        intent = request.get("intent", "").lower()
        actions: List[Action] = []
        if "send" in intent:
            actions.append(Action("act_1", "send_email", self.engine_id, request))
        elif "attachment" in intent:
            actions.append(Action("act_1", "fetch_attachments", self.engine_id, request))
        else:
            actions.append(Action("act_1", "read_emails", self.engine_id, request))

        return ExecutionPlan("plan_email", intent, actions, len(actions))

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

            if cap == "send_email":
                res = self.adapter.send_email(params.get("recipient", "user@example.com"), params.get("subject", "Hello"), params.get("body", "Body"))
                data = {"status": "sent"}
            elif cap == "read_emails":
                emails = self.adapter.read_latest_emails(params.get("sender"))
                res = f"Found {len(emails)} emails."
                data = {"emails": emails}
            elif cap == "fetch_attachments":
                attachment_path = self.adapter.download_attachment(params.get("email_id", "1"), params.get("attachment", "report.pdf"))
                res = f"Downloaded attachment to {attachment_path}"
                data = {"file_path": attachment_path}
            else:
                res = "Email operation complete."
                data = {}

            return ActionResult(True, action.action_id, self.engine_id, str(res), data, execution_time=time.time() - start_time)
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_email", self.engine_id, f"Email Engine error: {error}", error=str(error))

    def shutdown(self) -> None:
        self.initialized = False
