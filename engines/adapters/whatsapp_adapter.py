"""
WhatsApp App Adapter interfacing with WhatsApp Web automation.
"""
from typing import Dict, Any, Optional
from engines.adapters.base import BaseAdapter
import actions

class WhatsAppAdapter(BaseAdapter):
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "driver": "Microsoft Edge Selenium"}

    def login(self) -> str:
        return actions.whatsapp_login()

    def send_message(self, target: str, text: str) -> str:
        return actions.whatsapp_send_msg(target, text)

    def send_file(self, target: str, file_path: Optional[str] = None) -> str:
        return actions.whatsapp_send_file_action(target, file_path)

    def get_unreads(self) -> str:
        return actions.whatsapp_unreads_action()

    def auto_reply(self, mode: str, text: str = "") -> str:
        return actions.whatsapp_auto_reply_action(f"{mode} {text}".strip())

    def read_last(self, target: str) -> str:
        return actions.whatsapp_read_last_action(target)

    def get_status(self, target: str) -> str:
        return actions.whatsapp_status_action(target)

    def trigger_call(self, target: str, call_type: str = "voice") -> str:
        cmd = f"whatsapp {call_type} call {target}" if call_type == "video" else f"whatsapp call {target}"
        return actions.whatsapp_call_action(cmd)

    def broadcast(self, targets_str: str, text: str) -> str:
        return actions.whatsapp_broadcast_action(targets_str, text)

    def mute_chat(self, target: str) -> str:
        return actions.whatsapp_mute_action(target)

    def logout(self) -> str:
        return actions.whatsapp_logout_action()
