"""
Unit tests for application schedule parsing and execution.
"""
import unittest
from unittest.mock import patch
from nlp_engine import translate_to_command
from engines.whatsapp.engine import WhatsAppEngine
from engines.system.engine import SystemEngine

class TestAppScheduling(unittest.TestCase):

    def test_nlp_app_schedule_translation(self):
        self.assertEqual(translate_to_command("open whatsapp in 10 sec"), "open whatsapp in 10 sec")
        self.assertEqual(translate_to_command("launch chrome after 30 seconds"), "open chrome after 30 seconds")
        self.assertEqual(translate_to_command("close spotify in 1 minute"), "close spotify in 1 minute")
        self.assertEqual(translate_to_command("start calculator in 5 sec"), "open calculator in 5 sec")

    @patch("actions.add_jarvis_schedule")
    @patch("actions.open_app")
    def test_whatsapp_engine_intercepts_schedule(self, mock_open_app, mock_add_schedule):
        mock_add_schedule.return_value = "Scheduled Task"
        engine = WhatsAppEngine()
        engine.initialize()

        plan = engine.plan({"intent": "open whatsapp in 10 sec"})
        self.assertEqual(len(plan.actions), 1)
        action = plan.actions[0]
        self.assertEqual(action.capability, "schedule_action")
        self.assertEqual(action.parameters["command"], "open whatsapp")

        res = engine.execute(action)
        self.assertTrue(res.success)
        mock_add_schedule.assert_called_once()
        mock_open_app.assert_not_called()

    @patch("actions.add_jarvis_schedule")
    @patch("actions.close_app")
    def test_system_engine_intercepts_app_close_schedule(self, mock_close_app, mock_add_schedule):
        mock_add_schedule.return_value = "Scheduled Task"
        engine = SystemEngine()
        engine.initialize()

        plan = engine.plan({"intent": "close notepad in 30 sec"})
        self.assertEqual(len(plan.actions), 1)
        action = plan.actions[0]
        self.assertEqual(action.capability, "schedule_power")
        self.assertEqual(action.parameters["command"], "close notepad")

        res = engine.execute(action)
        self.assertTrue(res.success)
        mock_add_schedule.assert_called_once()
        mock_close_app.assert_not_called()

if __name__ == "__main__":
    unittest.main()
