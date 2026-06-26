# Jarvis Project Progress Log

## Project Objective
Create a local, rule-based Jarvis command assistant in Python that has full PC access and runs locally on the user's PC.

## Current Status
We have successfully resolved the UWP window-snapping and focus issue (tested with WhatsApp Beta) by refactoring the window matching and window manipulation system in `actions.py` to use native Win32 window enumeration in Python.

## Completed Tasks
- [x] Designed the architecture and execution flow.
- [x] Created `config.json` with default application paths, whitelists, and updated macro profiles.
- [x] Created `actions.py` containing PC automation logic.
- [x] Created `main.py` containing interactive console routing.
- [x] Downloaded and Installed Python 3.11.9.
- [x] Added Python to the system environment PATH.
- [x] Verified python syntax/execution on `main.py` and `actions.py`.
- [x] Created `run.bat` executable batch file for quick launch.
- [x] **GUI Search Launch Feature**: Start Menu keypress simulation.
- [x] **Close Application Feature**: Process termination command.
- [x] **Bulk App Profiles (Macros)**: Mapped workspace profiles in `config.json`.
- [x] **Web Link Integration**: Enhanced background launcher to recognize URL schemes.
- [x] **Close Current App Feature**: Added `close current app`.
- [x] **Window Control Actions**: Added global minimize/maximize commands and current active window minimize/maximize commands.
- [x] **Specific App Window Controls**: Added `maximize <app_name>` and `minimize <app_name>`.
- [x] **Timed/Scheduled Controls**: Mapped `open <app> in <time>` and `close <app> in <time>`. Spawns non-blocking background daemon threads.
- [x] **Window Layout Snapping**: Mapped `snap <app> <direction>` (left, right, top, bottom) using native Win32 window handles.
- [x] **Smart App Switching**: Mapped `switch to <app_name>` or `focus <app_name>` to bring minimized background apps to active focus.
- [x] **Audio Volume Control**: Mapped `mute/unmute <app>` and `volume <app> <0-100>` (supports `master` volume and per-app audio sessions using `pycaw` WASAPI wrapper).
- [x] **UWP / Windows Store App Window Fix**: Refactored `actions.py` window manipulation actions (`maximize_app`, `minimize_app`, `snap_app`, `switch_to_app`, `close_current_app`, `minimize_current_app`, `maximize_current_app`) to use native ctypes-based Win32 window enumeration. This correctly resolves UWP host-frame window mapping (`ApplicationFrameHost.exe`).
- [x] **Global Activation Hotkey**: Integrated a background Win32 global hotkey listener (`Ctrl+Alt+J`) in `main.py` that automatically restores and focuses the Jarvis terminal window on demand from anywhere in OS.
- [x] **Windows Desktop Launch Shortcut**: Programmed and deployed a native Windows shortcut (`Jarvis.lnk`) on the user's Desktop that targets `run.bat` and registers a global system hotkey (`Ctrl+Alt+J`) to launch the assistant instantly from anywhere in the OS, even when closed.
- [x] **Single-Instance Mutex Enforcement**: Added named mutex verification to [main.py](file:///e:/orion/main.py) to prevent launching duplicate terminal windows, automatically focusing the existing active instance when key combo is pressed while open.
- [x] **Clean CLI & High-Tech ANSI Colors**: Cleared console clutter on startup by hiding the massive help block. Grouped and colored help commands dynamically using native Windows Virtual Terminal Processing, styling the `[USER]:` and `[JARVIS]:` headers for a premium, professional user interface.
- [x] **Anti-Lock Jiggler (NEW)**: Added `keep awake` and `stop awake` background thread simulation of virtual `F15` keypresses to prevent screen locking/sleeping when user steps away.
- [x] **Display Brightness controls (NEW)**: Built `brightness <0-100>` using a PowerShell CimInstance query to set monitor brightness level.
- [x] **System Power Commands (NEW)**: Built `sleep pc` (via native `SetSuspendState`), `restart pc` and `shutdown pc` (via shell command wrappers).
- [x] **Multimedia Control Keys (NEW)**: Built global play/pause (`play` / `pause`) and skip track (`next` / `skip` / `previous`) simulation using standard multimedia key events.
- [x] **Battery Diagnostics Log (NEW)**: Built `battery status` which reads and displays charging states and time-remaining values directly from kernel32 power status API.
- [x] **Simple Windows Utility Controls (NEW)**: Built 10 new utility controls (Recycle Bin empty, display sleep, dark/light theme, microphone mute/unmute status, screenshot capture with fast GDI Win32 API, clipboard clear, virtual desktop switchers, settings deep-links, resource usage monitor, and volume status reports).
- [x] **Additional Windows Utility Controls (NEW)**: Built 7 more utility controls (idle time detector, Wi-Fi SSID/signal status, multi-drive storage breakdown, RAM optimization, process termination by PID, copying absolute paths to clipboard, and month calendar/time-date reports).
- [x] **Universal Task Scheduler & Alarm System (NEW)**: Deployed a background daemon thread linked to `schedules.json` to handle alarm notifications and schedule any supported Jarvis command at specific/recurring times.
- [x] **WhatsApp Web Automation (NEW)**: Deployed Microsoft Edge Selenium Webdriver automation with persistent user profile sessions. Supports headed QR code login authentication and fully automated text messaging to contact names or phone numbers (quotes optional). Fully integrated into the Jarvis command parsing and persistent scheduler system.
- [x] **WhatsApp Message Scheduler (NEW)**: Implemented specialized direct WhatsApp message scheduling commands (absolute, relative, and recurring layouts) that translate natural language schedule directives into standard background task schedules in `schedules.json`.
- [x] **Advanced WhatsApp Web Automations (NEW)**: Integrated 9 advanced Selenium features (unreads scanner, mute/unmute toggle, online/offline status inspector, voice/video call triggers, sequential contact broadcasting, last message reader, background auto-reply loop thread, and secure signout) and added CLI command routes.
- [x] **Visual File Picker Integration (NEW)**: Integrated a native topmost Windows File Picker (Tkinter + PowerShell Dialog fallback + Console fallback) to make file sends simple and quote-optional from the CLI.
- [x] **Keypress-Prioritized Send Optimization (NEW)**: Refactored the selenium media send function to prioritize active element Enter keypresses (targeting the caption text box) with robust backup button click and JavaScript execution strategies.
- [x] **Local NLP Translation Engine (NEW)**: Implemented [nlp_engine.py](file:///e:/orion/nlp_engine.py) to parse and map conversational natural language prompts (e.g. "don't sleep", "mute Chrome", "whatsapp Dad saying running late", "schedule clean temp in 10 minutes") into correct Jarvis CLI commands.
- [x] **WhatsApp Call Regex Precedence & Hinglish Expansion**: Resolved issue where "whatsapp call to mummy" was greedily intercepted by generic messaging rules. Rearranged match order, and expanded Hinglish voice/video call patterns (e.g., "mummy ko whatsapp call karo/lagao") to support optional "whatsapp" prefixing.
- [x] **Display Brightness & Website Translation Support**: Integrated robust display brightness matching (e.g., "set brightness 0", "adjust brightness level to 10") and direct website launching (e.g., "open youtube.com", "go to google.com") in [nlp_engine.py](file:///e:/orion/nlp_engine.py). Evaluated these before generic message matching to avoid greedy overlap.
- [x] **Microphone & Wi-Fi Synonym Expansion**: Added casual synonyms for recording microphone controls (e.g., "mute microphone", "microphone band karo") and network signal/connection reports (e.g., "wifi status", "network details") to the synonyms mapping list.
- [x] **Fuzzy Spelling Correction Module**: Built a local, dictionary-based spelling corrector inside [nlp_engine.py](file:///e:/orion/nlp_engine.py) using the built-in `difflib` module. Automatically fixes spelling mistakes in core Jarvis command keywords (e.g. "whatsap", "brightnes", "rebot", "screnshot", "messege") before matching rules, while maintaining contact names and custom parameters intact.
- [x] **Protected Action Word Safeguards & Awake Deactivation**: Protected action verbs (e.g., "deactivate", "disable", "activate", "enable") in the `KEYWORDS` list to prevent false-positive fuzzy corrections (such as "deactivate" correcting to "active"). Added support for multiple conversational keep-awake deactivation prompts (e.g., "deactivate awake", "disable keep awake", "turn off keep awake" $\rightarrow$ `stop awake`).
- [x] **App Focus & Bring Window to Front Support**: Protected focus-related verbs (e.g., "bring", "front", "focus") in the keywords dictionary. Added regex translation rules mapping conversational window-focusing requests (e.g., "bring chat gpt front", "focus on excel", "switch focus to word") directly to standard `switch to <app>` commands.
- [x] **Command Verb Safeguards on WhatsApp Messages (NEW)**: Expanded WhatsApp generic message regex checks to exclude active command verbs (e.g. "switch", "focus", "bring", "open", "close", "run", "call", "video call") from matching as targets or messages, resolving the bug where direct focus commands (like "swith to antigravity" or "switch to chrome") were greedily captured as WhatsApp text messages.
- [x] **Arrow-Key Navigable Help Menu (NEW)**: Built a dynamic console menu browser in [main.py](file:///e:/orion/main.py) using `msvcrt` and cursor-hiding ANSI escapes. Allows category browsing with Up/Down arrows and Enter.
- [x] **Categorized Help Menu & Sub-Matrices (NEW)**: Replaced the giant 50-line menu with structured categories (`help system`, `help apps`, `help schedule`, `help media`, `help whatsapp`, `help web`, and `help all`).
- [x] **Fuzzy Auto-Suggestions Fallback (NEW)**: Replaced the intrusive verbal/blocking Y/N shell prompt with a clean, color-coded suggestion engine that offers alternative matches (e.g., `Did you mean: 'status'?`) and falls back cleanly without interrupting the input stream.
- [x] **CLI Command Spelling Correction (NEW)**: Added `"help"`, `"commands"`, `"exit"`, and `"quit"` to the keywords mapping list to automatically handle typos in control words (e.g., `hlp` -> `help`).


## Tasks In Progress
- None.

## Remaining Tasks
- None.
