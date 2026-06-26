# WhatsApp Automation

This directory is dedicated to the WhatsApp automation module for the Jarvis Assistant.

## Suggested Features

1. **Send Message to Number (Direct Protocol)**: Open a chat with any phone number instantly using the official `whatsapp://send?phone=NUMBER` protocol or web URL redirect.
2. **Send Message to Contact by Name**: Automate the Windows Desktop WhatsApp UI (simulating `Ctrl+F` or `Ctrl+N` to search/start a chat, typing the contact's name, selecting them, typing the message, and pressing Enter).
3. **Schedule Message Delivery**: Schedule messages to be sent later by integrating with the Jarvis persistent scheduler database (e.g., `schedule "whatsapp message to John Doe text Hello" at 10:00`).
4. **Send Media / Attachments**: Automate clicking the attachment clip, pasting a path, and sending images/documents to a chat.
5. **Bulk Message Broadcast**: Deliver a single message to a list of pre-configured contacts or numbers.
6. **Trigger Voice / Video Call**: Auto-initiate calls to specified contacts.
7. **Read Unread Notifications**: Detect the presence of new incoming WhatsApp message notifications or taskbar count badges.
8. **Auto-Reply Mode**: A simple foreground automation script that polls the screen or listens for hotkeys to send preset away-messages.
