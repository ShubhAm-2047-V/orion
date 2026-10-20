"""
Unit Tests for BaseEngine Contract and Data Models.
"""
import unittest
from engines.base import BaseEngine, Action, ActionResult, ValidationResult, ExecutionPlan, Capability

class DummyEngine(BaseEngine):
    engine_id = "dummy"
    name = "Dummy Engine"
    description = "Engine for testing contracts"
    capabilities = ["dummy_action"]

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def health_check(self) -> dict:
        return {"status": "ok"}

    def can_handle(self, intent: str, context=None) -> bool:
        return "dummy" in intent.lower()

    def plan(self, request: dict) -> ExecutionPlan:
        action = Action("act_1", "dummy_action", self.engine_id, request)
        return ExecutionPlan("plan_dummy", request.get("intent", ""), [action], 1)

    def validate(self, action: Action) -> ValidationResult:
        if action.capability == "dummy_action":
            return ValidationResult(True)
        return ValidationResult(False, "Invalid capability")

    def execute(self, action: Action) -> ActionResult:
        return ActionResult(True, action.action_id, self.engine_id, "Dummy action executed.")

    def handle_error(self, error: Exception) -> ActionResult:
        return ActionResult(False, "err_dummy", self.engine_id, str(error))

    def shutdown(self) -> None:
        self.initialized = False

class TestBaseEngineContract(unittest.TestCase):
    def test_engine_contract(self):
        engine = DummyEngine()
        self.assertTrue(engine.initialize())
        self.assertEqual(engine.health_check()["status"], "ok")
        self.assertTrue(engine.can_handle("test dummy action"))
        self.assertFalse(engine.can_handle("unrelated request"))

        plan = engine.plan({"intent": "test dummy"})
        self.assertEqual(len(plan.actions), 1)
        action = plan.actions[0]
        self.assertEqual(action.capability, "dummy_action")

        val_res = engine.validate(action)
        self.assertTrue(val_res.is_valid)

        exec_res = engine.execute(action)
        self.assertTrue(exec_res.success)
        self.assertEqual(exec_res.message, "Dummy action executed.")

        engine.shutdown()
        self.assertFalse(engine.initialized)

if __name__ == "__main__":
    unittest.main()
