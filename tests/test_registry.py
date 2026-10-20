"""
Unit Tests for EngineRegistry and Auto-Discovery.
"""
import unittest
from engines.registry import EngineRegistry
from engines.base import BaseEngine

class TestEngineRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = EngineRegistry()

    def test_auto_discovery(self):
        self.registry.discover_and_register_all()
        registered = self.registry.list()
        self.assertGreaterEqual(len(registered), 17)

        engine_ids = [e.engine_id for e in registered]
        expected = [
            "browser", "file", "code", "email", "calendar", "music",
            "whatsapp", "telegram", "youtube", "spotify", "system",
            "settings", "search", "vision", "voice", "memory", "notification"
        ]
        for engine_id in expected:
            self.assertIn(engine_id, engine_ids, f"Engine '{engine_id}' should be auto-discovered")

    def test_find_by_capability(self):
        self.registry.discover_and_register_all()
        wa_engines = self.registry.find_by_capability("whatsapp_send_msg")
        self.assertTrue(any(e.engine_id == "whatsapp" for e in wa_engines))

    def test_health_check_all(self):
        self.registry.discover_and_register_all()
        health = self.registry.health_check_all()
        self.assertIn("system", health)
        self.assertIn("whatsapp", health)

if __name__ == "__main__":
    unittest.main()
