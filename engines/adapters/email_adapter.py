"""
Email Provider Adapter for JARVIS.
"""
from typing import Dict, Any, List
from engines.adapters.base import BaseAdapter

class EmailAdapter(BaseAdapter):
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "provider": "Email Adapter"}

    def send_email(self, recipient: str, subject: str, body: str) -> str:
        return f"Email sent successfully to '{recipient}' with subject '{subject}'."

    def read_latest_emails(self, sender: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        return [{
            "id": "email_101",
            "from": sender or "john@example.com",
            "subject": "Project Report Attachment",
            "body": "Here is the summary attachment.",
            "attachments": ["summary_report.txt"]
        }]

    def download_attachment(self, email_id: str, attachment_name: str) -> str:
        return f"C:\\Users\\SHUBHAM\\Downloads\\{attachment_name}"
