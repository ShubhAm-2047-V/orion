"""
Base Engine Interface and Data Contracts for JARVIS Engine Subsystem.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import time

@dataclass
class Capability:
    name: str
    description: str
    parameters: Dict[str, str] = field(default_factory=dict)

@dataclass
class Action:
    action_id: str
    capability: str
    engine_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    is_valid: bool
    reason: Optional[str] = None

@dataclass
class ActionResult:
    success: bool
    action_id: str
    engine_id: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0

@dataclass
class ExecutionPlan:
    plan_id: str
    request: str
    actions: List[Action]
    estimated_steps: int

class BaseEngine(ABC):
    """
    Abstract Base Class for all JARVIS Specialized App Engines.
    Every engine must inherit from BaseEngine and implement its abstract contract.
    """
    engine_id: str = "base_engine"
    name: str = "Base Engine"
    description: str = "Base interface for JARVIS engines"
    capabilities: List[str] = []

    def __init__(self):
        self.initialized: bool = False

    @abstractmethod
    def initialize(self) -> bool:
        """Initializes engine resources and adapters."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Returns health status of the engine and its adapters."""
        pass

    @abstractmethod
    def can_handle(self, intent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Determines whether this engine can fulfill the user request/intent."""
        pass

    @abstractmethod
    def plan(self, request: Dict[str, Any]) -> ExecutionPlan:
        """Creates an ExecutionPlan containing actions to fulfill the request."""
        pass

    @abstractmethod
    def validate(self, action: Action) -> ValidationResult:
        """Validates action parameters before execution."""
        pass

    @abstractmethod
    def execute(self, action: Action) -> ActionResult:
        """Executes a single action and returns ActionResult."""
        pass

    @abstractmethod
    def handle_error(self, error: Exception) -> ActionResult:
        """Structured error handler when execution fails."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleanly releases any active resources/drivers."""
        pass
