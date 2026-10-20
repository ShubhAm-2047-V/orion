"""
Thread-safe TTL Cache for JARVIS High-Frequency Operations.
"""
import time
import threading
from typing import Any, Dict, Optional, Callable

class TTLCache:
    """
    In-memory thread-safe TTL Cache for expensive OS diagnostics, hardware checks,
    and API queries.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTLCache, cls).__new__(cls)
            cls._instance._store: Dict[str, Dict[str, Any]] = {}
            cls._instance._lock = threading.Lock()
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if time.time() > entry["expires_at"]:
                del self._store[key]
                return None
            return entry["value"]

    def set(self, key: str, value: Any, ttl_seconds: float = 3.0) -> None:
        with self._lock:
            self._store[key] = {
                "value": value,
                "expires_at": time.time() + ttl_seconds
            }

    def memoize(self, key: str, ttl_seconds: float, func: Callable[[], Any]) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        val = func()
        self.set(key, val, ttl_seconds=ttl_seconds)
        return val

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
