"""
Unit Tests for Deep Human Natural Language Understanding Engine (nlp_engine.py).
"""
import unittest
from nlp_engine import translate_to_command, correct_spelling

class TestNLPEngineDeepTraining(unittest.TestCase):
    def test_polite_prefix_and_suffix_stripping(self):
        self.assertEqual(translate_to_command("jarvis please check system status"), "status")
        self.assertEqual(translate_to_command("could you please turn off screen for me asap"), "turn off screen")
        self.assertEqual(translate_to_command("hey jarvis please take screenshot ok"), "screenshot")

    def test_hinglish_phrases_understanding(self):
        self.assertEqual(translate_to_command("computer band karo"), "shutdown pc")
        self.assertEqual(translate_to_command("time batao"), "time")
        self.assertEqual(translate_to_command("screen ka photo lo"), "screenshot")
        self.assertEqual(translate_to_command("temp clean karo"), "clean temp")
        self.assertEqual(translate_to_command("recycle bin khali karo"), "empty trash")
        self.assertEqual(translate_to_command("wifi settings kholo"), "open wifi settings")

    def test_typo_fuzzy_spelling_corrections(self):
        self.assertEqual(correct_spelling("brightnes"), "brightness")
        self.assertEqual(correct_spelling("screnshot"), "screenshot")
        self.assertEqual(correct_spelling("rebot"), "reboot")
        self.assertEqual(translate_to_command("rebot pc"), "restart pc")
        self.assertEqual(correct_spelling("whatsap"), "whatsapp")

    def test_domain_engine_natural_language_mapping(self):
        self.assertEqual(translate_to_command("send email to test@example.com"), "send email to test@example.com")
        self.assertEqual(translate_to_command("check whatsapp unreads"), "whatsapp unreads")
        self.assertEqual(translate_to_command("open youtube"), "open youtube")
        self.assertEqual(translate_to_command("open wifi settings"), "open wifi settings")

    def test_power_schedule_translations(self):
        self.assertEqual(translate_to_command("shutdown the pc after 30 sec"), "shutdown pc in 30 sec")
        self.assertEqual(translate_to_command("turn off computer in 5 minutes"), "shutdown pc in 5 minutes")

if __name__ == "__main__":
    unittest.main()
