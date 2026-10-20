"""
Base Adapter Interface for JARVIS App Engines.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAdapter(ABC):
    """
    Decouples specialized engine decision logic from underlying OS/API calls.
    """
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        pass
