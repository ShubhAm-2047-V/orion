"""
Unit tests for power scheduling and natural language power commands.
"""
import unittest
from unittest.mock import patch, MagicMock
from nlp_engine import translate_to_command
from engines.system.engine import SystemEngine

class TestPowerScheduling(unittest.TestCase):

    def test_nlp_power_schedule_translation(self):
        self.assertEqual(translate_to_command("shutdown the pc after 30 sec"), "shutdown pc in 30 sec")
        self.assertEqual(translate_to_command("turn off computer in 5 minutes"), "shutdown pc in 5 minutes")
        self.assertEqual(translate_to_command("power off the pc after 10 seconds"), "shutdown pc in 10 seconds")
        self.assertEqual(translate_to_command("restart the computer in 2 mins"), "restart pc in 2 mins")
        self.assertEqual(translate_to_command("sleep pc after 1 hour"), "sleep pc in 1 hour")

    @patch("actions.add_jarvis_schedule")
    @patch("actions.set_power_state")
    def test_system_engine_intercepts_delayed_shutdown(self, mock_set_power, mock_add_schedule):
        mock_add_schedule.return_value = "Scheduled Task"
        engine = SystemEngine()
        engine.initialize()

        plan = engine.plan({"intent": "shutdown the pc after 30 sec"})
        self.assertEqual(len(plan.actions), 1)
        action = plan.actions[0]
        self.assertEqual(action.capability, "schedule_power")
        self.assertEqual(action.parameters["command"], "shutdown pc")

        res = engine.execute(action)
        self.assertTrue(res.success)
        mock_add_schedule.assert_called_once()
        mock_set_power.assert_not_called()

    @patch("actions.set_power_state")
    def test_system_engine_handles_immediate_shutdown(self, mock_set_power):
        mock_set_power.return_value = "Shutdown command sent to OS."
        engine = SystemEngine()
        engine.initialize()

        plan = engine.plan({"intent": "shutdown pc"})
        self.assertEqual(len(plan.actions), 1)
        action = plan.actions[0]
        self.assertEqual(action.capability, "shutdown_pc")

        res = engine.execute(action)
        self.assertTrue(res.success)
        mock_set_power.assert_called_once_with("shutdown")

if __name__ == "__main__":
    unittest.main()
