"""
Structured Error Hierarchy for JARVIS Modular Multi-Engine System.
"""

class JARVISException(Exception):
    """Base exception for all JARVIS errors."""
    def __init__(self, message: str, engine_id: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.engine_id = engine_id
        self.details = details or {}

class EngineError(JARVISException):
    """Exception raised for errors occurring within an engine."""
    pass

class EngineInitializationError(EngineError):
    """Exception raised when an engine fails to initialize."""
    pass

class CapabilityNotFoundError(EngineError):
    """Exception raised when no engine supports the requested capability."""
    pass

class ValidationFailedError(EngineError):
    """Exception raised when action validation fails."""
    pass

class PermissionDeniedError(JARVISException):
    """Exception raised when permission check fails for a sensitive/critical action."""
    pass

class AdapterError(JARVISException):
    """Exception raised when an underlying app adapter fails."""
    pass

class RouterError(JARVISException):
    """Exception raised when routing or multi-engine pipeline execution fails."""
    pass
