"""
Permission Manager & Security Layer for JARVIS System Operations.
"""
from enum import Enum
from typing import Dict, Any, Optional, Callable
from engines.shared.errors import PermissionDeniedError
from engines.shared.logging import get_logger

logger = get_logger("permissions")

class RiskLevel(Enum):
    NORMAL = 1
    SENSITIVE = 2
    CRITICAL = 3

class PermissionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PermissionManager, cls).__new__(cls)
            cls._instance.capability_risks: Dict[str, RiskLevel] = {}
            cls._instance.user_confirmation_callback: Optional[Callable[[str, RiskLevel], bool]] = None
            cls._instance._register_default_risks()
        return cls._instance

    def _register_default_risks(self):
        # Critical actions
        self.capability_risks["shutdown_pc"] = RiskLevel.CRITICAL
        self.capability_risks["restart_pc"] = RiskLevel.CRITICAL
        self.capability_risks["empty_recycle_bin"] = RiskLevel.CRITICAL
        self.capability_risks["kill_pid"] = RiskLevel.CRITICAL
        self.capability_risks["terminal_exec"] = RiskLevel.CRITICAL
        self.capability_risks["clear_memory"] = RiskLevel.CRITICAL

        # Sensitive actions
        self.capability_risks["clean_temp"] = RiskLevel.SENSITIVE
        self.capability_risks["whatsapp_broadcast"] = RiskLevel.SENSITIVE
        self.capability_risks["whatsapp_logout"] = RiskLevel.SENSITIVE
        self.capability_risks["send_email"] = RiskLevel.SENSITIVE
        self.capability_risks["telegram_send_msg"] = RiskLevel.SENSITIVE

    def register_risk_level(self, capability: str, risk_level: RiskLevel) -> None:
        self.capability_risks[capability] = risk_level

    def get_risk_level(self, capability: str) -> RiskLevel:
        return self.capability_risks.get(capability, RiskLevel.NORMAL)

    def set_confirmation_callback(self, callback: Callable[[str, RiskLevel], bool]) -> None:
        self.user_confirmation_callback = callback

    def authorize(self, capability: str, params: Optional[Dict[str, Any]] = None) -> bool:
        risk = self.get_risk_level(capability)
        logger.info(f"Checking permission for capability '{capability}' (Risk Level: {risk.name})")

        if risk == RiskLevel.NORMAL:
            return True

        if risk in (RiskLevel.SENSITIVE, RiskLevel.CRITICAL):
            if self.user_confirmation_callback:
                approved = self.user_confirmation_callback(capability, risk)
                if not approved:
                    raise PermissionDeniedError(
                        f"Action '{capability}' requiring {risk.name} permission was denied by user/policy.",
                        details={"capability": capability, "risk_level": risk.name}
                    )
                return True
            # Default auto-approval if no interactive callback is registered (non-blocking CLI mode)
            logger.info(f"Action '{capability}' authorized automatically under default security policy.")
            return True

        return True
