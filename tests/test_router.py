"""
Unit Tests for EngineRouter & Multi-Engine Pipeline Workflows.
"""
import unittest
from engines.registry import EngineRegistry
from engines.router import EngineRouter

class TestEngineRouter(unittest.TestCase):
    def setUp(self):
        self.registry = EngineRegistry()
        self.registry.discover_and_register_all()
        self.router = EngineRouter(registry=self.registry)

    def test_single_engine_routing(self):
        results = self.router.route_request("system status")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].engine_id, "system")

    def test_whatsapp_routing(self):
        results = self.router.route_request("whatsapp unreads")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].engine_id, "whatsapp")

    def test_multi_engine_pipeline_workflow(self):
        # Pipeline request: "read latest email from John then clean temp then store memory"
        request = "read latest email from John then clean temp then remember note"
        results = self.router.route_request(request)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].engine_id, "email")
        self.assertEqual(results[1].engine_id, "file")
        self.assertEqual(results[2].engine_id, "memory")

        for res in results:
            self.assertTrue(res.success)

if __name__ == "__main__":
    unittest.main()
