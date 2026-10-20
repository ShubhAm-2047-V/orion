"""
Memory Manager for JARVIS (Short-Term Conversation Context & Persistent Knowledge).
Optimized with deque ring-buffer for O(1) memory management.
"""
import time
from collections import deque
from typing import Any, Dict, List, Optional

class MemoryManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
            cls._instance.conversation_history = deque(maxlen=100)
            cls._instance.persistent_store: Dict[str, Any] = {}
            cls._instance.engine_states: Dict[str, Any] = {}
        return cls._instance

    def add_conversation(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        entry = {
            "timestamp": time.time(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.conversation_history.append(entry)

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        history_list = list(self.conversation_history)
        return history_list[-limit:]

    def set_key(self, key: str, value: Any) -> None:
        self.persistent_store[key] = value

    def get_key(self, key: str, default: Any = None) -> Any:
        return self.persistent_store.get(key, default)

    def set_engine_state(self, engine_id: str, state: Dict[str, Any]) -> None:
        self.engine_states[engine_id] = state

    def get_engine_state(self, engine_id: str) -> Dict[str, Any]:
        return self.engine_states.get(engine_id, {})

    def clear(self) -> None:
        self.conversation_history.clear()
        self.persistent_store.clear()
        self.engine_states.clear()
