"""
Event Bus for Decoupled Inter-Engine Communication.
"""
from typing import Callable, Dict, List, Any
import threading

class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._subscribers: Dict[str, List[Callable[[str, Any], None]]] = {}
            cls._instance._lock = threading.Lock()
        return cls._instance

    def subscribe(self, event_type: str, handler: Callable[[str, Any], None]) -> None:
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[str, Any], None]) -> None:
        with self._lock:
            if event_type in self._subscribers and handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)

    def publish(self, event_type: str, data: Any = None) -> None:
        with self._lock:
            handlers = list(self._subscribers.get(event_type, [])) + list(self._subscribers.get("*", []))
        
        for handler in handlers:
            try:
                handler(event_type, data)
            except Exception:
                pass
