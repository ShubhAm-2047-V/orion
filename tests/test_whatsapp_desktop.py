"""
Unit tests for WhatsApp Desktop App messaging and NLP translation.
"""
import unittest
from unittest.mock import patch
from nlp_engine import translate_to_command

class TestWhatsAppDesktop(unittest.TestCase):

    def test_send_to_contact_translation(self):
        self.assertEqual(
            translate_to_command("send hello to dad"),
            'whatsapp message to "dad" text "hello"'
        )
        self.assertEqual(
            translate_to_command("text good morning to mummy"),
            'whatsapp message to "mummy" text "good morning"'
        )
        self.assertEqual(
            translate_to_command("message happy birthday to alex"),
            'whatsapp message to "alex" text "happy birthday"'
        )

    @patch("whatsapp.automation.send_whatsapp_desktop_message")
    def test_whatsapp_message_dispatch_uses_desktop(self, mock_desktop):
        mock_desktop.return_value = "Successfully sent WhatsApp message to 'dad' via WhatsApp Desktop App."
        from whatsapp.automation import send_whatsapp_message
        
        res = send_whatsapp_message("dad", "hello")
        self.assertIn("WhatsApp Desktop App", res)
        mock_desktop.assert_called_once_with("dad", "hello")

if __name__ == "__main__":
    unittest.main()
