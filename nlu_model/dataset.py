"""
Training Dataset & Intent Catalog for Orion NLU Engine.
Contains hundreds of human language variations (English, Hindi, Marathi, Hinglish, typos, slang)
mapped to Orion's exact capability matrix and machine schemas.
"""
from typing import List, Dict, Any

TRAINING_DATA: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # INTENT: open_application (Engine: system / apps)
    # -------------------------------------------------------------
    {"text": "Hey open Chrome and search for best AI tools", "intent": "open_application_and_search", "engine": "browser", "action": "open_and_search", "params": {"app": "chrome", "query": "best AI tools"}},
    {"text": "bhai mere laptop ka calculator khol de", "intent": "open_application", "engine": "system", "action": "open_app", "params": {"app": "calculator"}},
    {"text": "calculator chalu kara lavkar", "intent": "open_application", "engine": "system", "action": "open_app", "params": {"app": "calculator"}},
    {"text": "open notepad please", "intent": "open_application", "engine": "system", "action": "open_app", "params": {"app": "notepad"}},
    {"text": "launch google chrome", "intent": "open_application", "engine": "browser", "action": "open_app", "params": {"app": "chrome"}},
    {"text": "open vscode editor", "intent": "open_application", "engine": "code", "action": "open_ide", "params": {"app": "antigravity"}},
    {"text": "open antigravity ide", "intent": "open_application", "engine": "code", "action": "open_ide", "params": {"app": "antigravity"}},
    {"text": "start task manager", "intent": "open_application", "engine": "system", "action": "open_app", "params": {"app": "taskmgr"}},
    {"text": "cmd kholo", "intent": "open_application", "engine": "system", "action": "open_app", "params": {"app": "cmd"}},
    {"text": "open powershell terminal", "intent": "open_application", "engine": "system", "action": "open_app", "params": {"app": "powershell"}},
    {"text": "can you please open explorer", "intent": "open_application", "engine": "system", "action": "open_app", "params": {"app": "explorer"}},
    {"text": "file manager ugada", "intent": "open_application", "engine": "system", "action": "open_app", "params": {"app": "explorer"}},
    {"text": "open chatgpt app", "intent": "open_application", "engine": "system", "action": "open_app", "params": {"app": "chatgpt"}},
    {"text": "spotify chalu karo gane sunna hai", "intent": "open_application", "engine": "music", "action": "open_app", "params": {"app": "spotify"}},

    # -------------------------------------------------------------
    # INTENT: close_application
    # -------------------------------------------------------------
    {"text": "close chrome browser", "intent": "close_application", "engine": "system", "action": "close_app", "params": {"app": "chrome"}},
    {"text": "band karo calculator", "intent": "close_application", "engine": "system", "action": "close_app", "params": {"app": "calculator"}},
    {"text": "notepad band kara bhau", "intent": "close_application", "engine": "system", "action": "close_app", "params": {"app": "notepad"}},
    {"text": "close current window", "intent": "close_application", "engine": "system", "action": "close_current_app", "params": {}},
    {"text": "close all programs right now", "intent": "close_application", "engine": "system", "action": "close_all", "params": {}},
    {"text": "kill spotify process", "intent": "close_application", "engine": "system", "action": "close_app", "params": {"app": "spotify"}},

    # -------------------------------------------------------------
    # INTENT: search_web
    # -------------------------------------------------------------
    {"text": "search for latest machine learning news", "intent": "search_web", "engine": "search", "action": "search_web", "params": {"query": "latest machine learning news"}},
    {"text": "google what is python 3.13 features", "intent": "search_web", "engine": "search", "action": "search_web", "params": {"query": "what is python 3.13 features"}},
    {"text": "dhoondho best mechanical keyboard", "intent": "search_web", "engine": "search", "action": "search_web", "params": {"query": "best mechanical keyboard"}},
    {"text": "google pe shodh kara weather in mumbai", "intent": "search_web", "engine": "search", "action": "search_web", "params": {"query": "weather in mumbai"}},
    {"text": "search top 10 movies of 2026", "intent": "search_web", "engine": "search", "action": "search_web", "params": {"query": "top 10 movies of 2026"}},

    # -------------------------------------------------------------
    # INTENT: open_website
    # -------------------------------------------------------------
    {"text": "open website github.com", "intent": "open_website", "engine": "browser", "action": "open_url", "params": {"url": "https://github.com"}},
    {"text": "website youtube.com", "intent": "open_website", "engine": "browser", "action": "open_url", "params": {"url": "https://youtube.com"}},
    {"text": "open reddit", "intent": "open_website", "engine": "browser", "action": "open_url", "params": {"url": "https://reddit.com"}},
    {"text": "open gmail inbox", "intent": "open_website", "engine": "browser", "action": "open_url", "params": {"url": "https://mail.google.com"}},

    # -------------------------------------------------------------
    # INTENT: system_status / diagnostics
    # -------------------------------------------------------------
    {"text": "check system status", "intent": "system_status", "engine": "system", "action": "system_status", "params": {}},
    {"text": "diagnostics report dikhao", "intent": "system_status", "engine": "system", "action": "system_status", "params": {}},
    {"text": "how is my computer doing", "intent": "system_status", "engine": "system", "action": "system_status", "params": {}},
    {"text": "pc status kasa ahe bagha", "intent": "system_status", "engine": "system", "action": "system_status", "params": {}},
    {"text": "battery status kya hai", "intent": "battery_status", "engine": "system", "action": "battery_status", "params": {}},
    {"text": "is my laptop charging", "intent": "battery_status", "engine": "system", "action": "battery_status", "params": {}},
    {"text": "battery kitni bachi hai", "intent": "battery_status", "engine": "system", "action": "battery_status", "params": {}},
    {"text": "storage space check karo", "intent": "disk_check", "engine": "system", "action": "disk_check", "params": {}},
    {"text": "disk space breakdown dikhao", "intent": "disk_check", "engine": "system", "action": "disk_check", "params": {}},
    {"text": "what is eating my ram", "intent": "top_processes", "engine": "system", "action": "top_processes", "params": {}},
    {"text": "top processes resource usage", "intent": "top_processes", "engine": "system", "action": "top_processes", "params": {}},
    {"text": "optimize memory free up ram", "intent": "optimize_memory", "engine": "system", "action": "optimize_memory", "params": {}},
    {"text": "ram boost karo", "intent": "optimize_memory", "engine": "system", "action": "optimize_memory", "params": {}},
    {"text": "how long has the pc been idle", "intent": "idle_time", "engine": "system", "action": "idle_time", "params": {}},

    # -------------------------------------------------------------
    # INTENT: control_volume & media
    # -------------------------------------------------------------
    {"text": "set volume to 60 percent", "intent": "control_volume", "engine": "settings", "action": "set_volume", "params": {"level": 60}},
    {"text": "aawaz 50 karo", "intent": "control_volume", "engine": "settings", "action": "set_volume", "params": {"level": 50}},
    {"text": "volume badha do thoda", "intent": "control_volume", "engine": "settings", "action": "volume_up", "params": {"step": 10}},
    {"text": "volume kam karo", "intent": "control_volume", "engine": "settings", "action": "volume_down", "params": {"step": 10}},
    {"text": "aawaz kami kara", "intent": "control_volume", "engine": "settings", "action": "volume_down", "params": {"step": 10}},
    {"text": "mute audio master", "intent": "control_volume", "engine": "settings", "action": "mute", "params": {"target": "master"}},
    {"text": "unmute sound", "intent": "control_volume", "engine": "settings", "action": "unmute", "params": {"target": "master"}},
    {"text": "mute microphone", "intent": "control_volume", "engine": "settings", "action": "mute_mic", "params": {}},
    {"text": "mic chalu karo", "intent": "control_volume", "engine": "settings", "action": "unmute_mic", "params": {}},
    {"text": "play next song", "intent": "media_playback", "engine": "music", "action": "next_track", "params": {}},
    {"text": "pause music playback", "intent": "media_playback", "engine": "music", "action": "pause", "params": {}},
    {"text": "previous track", "intent": "media_playback", "engine": "music", "action": "previous_track", "params": {}},

    # -------------------------------------------------------------
    # INTENT: system_power (Lock, Sleep, Screen, Power)
    # -------------------------------------------------------------
    {"text": "lock my pc screen immediately", "intent": "lock_pc", "engine": "system", "action": "lock_pc", "params": {}},
    {"text": "screen lock karo", "intent": "lock_pc", "engine": "system", "action": "lock_pc", "params": {}},
    {"text": "put pc to sleep mode", "intent": "sleep_pc", "engine": "system", "action": "sleep_pc", "params": {}},
    {"text": "pc ko sula do", "intent": "sleep_pc", "engine": "system", "action": "sleep_pc", "params": {}},
    {"text": "turn off screen display", "intent": "turn_off_screen", "engine": "system", "action": "turn_off_screen", "params": {}},
    {"text": "display band karo", "intent": "turn_off_screen", "engine": "system", "action": "turn_off_screen", "params": {}},
    {"text": "restart my computer", "intent": "restart_pc", "engine": "system", "action": "restart_pc", "params": {}},
    {"text": "shutdown the workstation", "intent": "shutdown_pc", "engine": "system", "action": "shutdown_pc", "params": {}},

    # -------------------------------------------------------------
    # INTENT: system_maintenance (Clean Temp, Empty Trash)
    # -------------------------------------------------------------
    {"text": "clean temp files", "intent": "clean_temp", "engine": "file", "action": "clean_temp", "params": {}},
    {"text": "delete temporary files and cache", "intent": "clean_temp", "engine": "file", "action": "clean_temp", "params": {}},
    {"text": "kachra saaf karo system ka", "intent": "clean_temp", "engine": "file", "action": "clean_temp", "params": {}},
    {"text": "empty recycle bin completely", "intent": "empty_trash", "engine": "file", "action": "empty_recycle_bin", "params": {}},
    {"text": "recycle bin khali karo", "intent": "empty_trash", "engine": "file", "action": "empty_recycle_bin", "params": {}},

    # -------------------------------------------------------------
    # INTENT: utilities (Screenshot, Clipboard, Keep Awake, Themes)
    # -------------------------------------------------------------
    {"text": "take a screenshot of desktop", "intent": "take_screenshot", "engine": "vision", "action": "screenshot", "params": {}},
    {"text": "screen capture karo", "intent": "take_screenshot", "engine": "vision", "action": "screenshot", "params": {}},
    {"text": "clear clipboard contents", "intent": "clear_clipboard", "engine": "system", "action": "clear_clipboard", "params": {}},
    {"text": "keep computer awake and start mouse jiggler", "intent": "keep_awake", "engine": "system", "action": "start_awake", "params": {}},
    {"text": "stop mouse jiggler allow sleep", "intent": "stop_awake", "engine": "system", "action": "stop_awake", "params": {}},
    {"text": "enable dark mode theme", "intent": "set_theme", "engine": "settings", "action": "set_theme", "params": {"theme": "dark"}},
    {"text": "light mode chalu karo", "intent": "set_theme", "engine": "settings", "action": "set_theme", "params": {"theme": "light"}},

    # -------------------------------------------------------------
    # INTENT: file_and_folder_operations (English + Grammatical Errors)
    # -------------------------------------------------------------
    {"text": "Create new folder name project files on desktop", "intent": "create_folder", "engine": "file", "action": "create_folder", "params": {"folder_name": "project files", "location": "desktop"}},
    {"text": "make a new folder called data analysis in documents", "intent": "create_folder", "engine": "file", "action": "create_folder", "params": {"folder_name": "data analysis", "location": "documents"}},
    {"text": "desktop pe ek naya folder banao backup naam se", "intent": "create_folder", "engine": "file", "action": "create_folder", "params": {"folder_name": "backup", "location": "desktop"}},
    {"text": "Create a Python file named hello.py and write a program that prints Hello World", "intent": "create_file_and_code", "engine": "code", "action": "create_file", "params": {"file_name": "hello.py", "file_type": "python", "content": "print('Hello World')", "language": "python"}},
    {"text": "create file test.js with console log hello", "intent": "create_file_and_code", "engine": "code", "action": "create_file", "params": {"file_name": "test.js", "file_type": "javascript", "content": "console.log('Hello');", "language": "javascript"}},
    {"text": "read file notes.txt", "intent": "read_file", "engine": "file", "action": "read_file", "params": {"file_name": "notes.txt"}},

    # -------------------------------------------------------------
    # INTENT: whatsapp_automation
    # -------------------------------------------------------------
    {"text": "whatsapp message to Shubham text hey let us meet tomorrow", "intent": "whatsapp_message", "engine": "whatsapp", "action": "send_msg", "params": {"target": "Shubham", "message": "hey let us meet tomorrow"}},
    {"text": "send whatsapp message to Mom saying I reached safely", "intent": "whatsapp_message", "engine": "whatsapp", "action": "send_msg", "params": {"target": "Mom", "message": "I reached safely"}},
    {"text": "whatsapp unreads check karo", "intent": "whatsapp_unreads", "engine": "whatsapp", "action": "get_unreads", "params": {}},
    {"text": "check unread whatsapp messages", "intent": "whatsapp_unreads", "engine": "whatsapp", "action": "get_unreads", "params": {}},
    {"text": "whatsapp call to John", "intent": "whatsapp_call", "engine": "whatsapp", "action": "call", "params": {"target": "John", "type": "voice"}},
    {"text": "whatsapp video call to Alex", "intent": "whatsapp_call", "engine": "whatsapp", "action": "call", "params": {"target": "Alex", "type": "video"}},
    {"text": "whatsapp status of Rahul", "intent": "whatsapp_status", "engine": "whatsapp", "action": "get_status", "params": {"target": "Rahul"}},
    {"text": "whatsapp send file to Vikas path e:/report.pdf", "intent": "whatsapp_send_file", "engine": "whatsapp", "action": "send_file", "params": {"target": "Vikas", "file_path": "e:/report.pdf"}},
    {"text": "whatsapp login", "intent": "whatsapp_login", "engine": "whatsapp", "action": "login", "params": {}},
    {"text": "whatsapp logout signout", "intent": "whatsapp_logout", "engine": "whatsapp", "action": "logout", "params": {}},

    # -------------------------------------------------------------
    # INTENT: code_and_database (Python, JS, SQL, Shell execution)
    # -------------------------------------------------------------
    {"text": "generate python code to fetch weather data from open-meteo api", "intent": "generate_code", "engine": "code", "action": "code_gen", "params": {"language": "python", "task": "fetch weather data from open-meteo api"}},
    {"text": "write sql query to get top 10 users ordered by creation date", "intent": "database_query", "engine": "code", "action": "sql_query", "params": {"query_type": "select", "table": "users", "order_by": "creation_date", "limit": 10}},
    {"text": "write powershell script to list all running services", "intent": "shell_command", "engine": "code", "action": "terminal_exec", "params": {"command": "Get-Service | Where-Object {$_.Status -eq 'Running'}"}},
    {"text": "generate javascript function to debounce input events", "intent": "generate_code", "engine": "code", "action": "code_gen", "params": {"language": "javascript", "task": "debounce input events"}},

    # -------------------------------------------------------------
    # INTENT: ambiguous_commands (Require clarifying questions)
    # -------------------------------------------------------------
    {"text": "Delete the old project", "intent": "ambiguous_delete", "engine": "file", "action": "clarify_ambiguity", "params": {"target": "old project"}, "ambiguous": True, "question": "Multiple projects exist. Which specific project folder do you want to delete?"},
    {"text": "Clean it", "intent": "ambiguous_clean", "engine": "system", "action": "clarify_ambiguity", "params": {}, "ambiguous": True, "question": "What would you like to clean? (Temporary cache files, Recycle Bin, or RAM memory?)"},
    {"text": "Send message", "intent": "ambiguous_message", "engine": "whatsapp", "action": "clarify_ambiguity", "params": {}, "ambiguous": True, "question": "Who would you like to send a message to, and what should the message say?"},
    {"text": "Open file", "intent": "ambiguous_open_file", "engine": "file", "action": "clarify_ambiguity", "params": {}, "ambiguous": True, "question": "Which file would you like to open? Please specify the file name or path."},
    {"text": "Remove files", "intent": "ambiguous_delete", "engine": "file", "action": "clarify_ambiguity", "params": {}, "ambiguous": True, "question": "Which specific files would you like to remove?"}
]
