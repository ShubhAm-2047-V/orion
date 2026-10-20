"""
Safety & Permission Engine for Orion NLU Model.
Implements risk classification, destructive command mitigation, prompt injection defense, and confirmation rules.
"""
import re
from typing import Dict, Any, Tuple, List
from engines.permissions import PermissionManager, RiskLevel

# Explicit allowlist of permissible system intents
PERMISSIBLE_INTENTS = {
    "open_application", "open_application_and_search", "close_application",
    "search_web", "open_website",
    "system_status", "battery_status", "disk_check", "top_processes", "optimize_memory", "idle_time",
    "control_volume", "media_playback",
    "lock_pc", "sleep_pc", "restart_pc", "shutdown_pc", "turn_off_screen",
    "clean_temp", "empty_trash", "take_screenshot", "clear_clipboard", "keep_awake", "stop_awake",
    "set_theme", "create_folder", "create_file_and_code", "read_file",
    "whatsapp_message", "whatsapp_send_file", "whatsapp_unreads", "whatsapp_call",
    "whatsapp_status", "whatsapp_broadcast", "whatsapp_login", "whatsapp_logout",
    "generate_code", "database_query", "shell_command",
    "ambiguous_delete", "ambiguous_clean", "ambiguous_message", "ambiguous_open_file"
}

# Prompt injection and jailbreak defense signatures
INJECTION_SIGNATURES = [
    r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|rules)",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"bypass\s+(security|safety|restrictions)",
    r"format\s+[a-z]:",
    r"del\s+/[sfq]\s+c:",
    r"rmdir\s+/[sq]\s+c:",
    r"drop\s+database",
    r"truncate\s+table"
]

class SafetyEvaluation:
    def __init__(self, is_safe: bool, risk_level: str, requires_confirmation: bool, reason: str = ""):
        self.is_safe = is_safe
        self.risk_level = risk_level  # NORMAL, SENSITIVE, CRITICAL
        self.requires_confirmation = requires_confirmation
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_safe": self.is_safe,
            "risk_level": self.risk_level,
            "requires_confirmation": self.requires_confirmation,
            "reason": self.reason
        }

def evaluate_command_safety(raw_input: str, intent: str, action: str, params: Dict[str, Any]) -> SafetyEvaluation:
    """
    Evaluates risk and authorization requirements for any parsed command.
    """
    # 1. Prompt Injection & Destructive Payload Check
    for pattern in INJECTION_SIGNATURES:
        if re.search(pattern, raw_input, re.IGNORECASE):
            return SafetyEvaluation(
                is_safe=False,
                risk_level="CRITICAL",
                requires_confirmation=True,
                reason="Potential prompt injection or destructive command attempt detected."
            )

    # 2. Allowlist Check
    if intent not in PERMISSIBLE_INTENTS:
        return SafetyEvaluation(
            is_safe=False,
            risk_level="CRITICAL",
            requires_confirmation=True,
            reason=f"Intent '{intent}' is not in the system's approved capability allowlist."
        )

    # 3. Critical Actions (Always require confirmation)
    critical_actions = {
        "shutdown_pc": "Shutdown will terminate all active programs and save states.",
        "restart_pc": "Restart will reboot the workstation.",
        "empty_recycle_bin": "Emptying trash will permanently delete unrecoverable files.",
        "kill_pid": "Terminating system PIDs could cause unsaved work loss.",
        "terminal_exec": "Terminal execution requires explicit review.",
        "ambiguous_delete": "Deletion without target confirmation risks data loss."
    }

    if action in critical_actions or intent in ("shutdown_pc", "restart_pc", "empty_trash", "ambiguous_delete"):
        reason = critical_actions.get(action, "Potentially destructive operation requires explicit user authorization.")
        return SafetyEvaluation(
            is_safe=True,
            risk_level="CRITICAL",
            requires_confirmation=True,
            reason=reason
        )

    # 4. Sensitive Actions (Requires review / audit log)
    sensitive_actions = {
        "clean_temp": "Cleans temporary files and caches.",
        "whatsapp_broadcast": "Transmits messages to multiple contacts simultaneously.",
        "whatsapp_logout": "Terminates active session and clears auth cookies.",
        "create_file": "Creates a file on the local filesystem.",
        "create_folder": "Creates a new folder."
    }

    if action in sensitive_actions or intent in ("clean_temp", "whatsapp_broadcast", "create_file_and_code"):
        return SafetyEvaluation(
            is_safe=True,
            risk_level="SENSITIVE",
            requires_confirmation=False,
            reason=sensitive_actions.get(action, "Sensitive action monitored under audit trail.")
        )

    # 5. Normal Safe Actions
    return SafetyEvaluation(
        is_safe=True,
        risk_level="NORMAL",
        requires_confirmation=False,
        reason="Operation is verified safe under standard permission policy."
    )
