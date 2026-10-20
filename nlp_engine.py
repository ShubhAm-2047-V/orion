import re
import difflib

# Deeply expanded dictionary of protected system keywords and engine capability terms
KEYWORDS = [
    "whatsapp", "message", "broadcast", "status", "online", "unreads", "unread", "login", "logout", "signout", "call", "video",
    "brightness", "volume", "mute", "unmute", "master", "audio", "speaker", "speakers", "microphone", "mic",
    "schedule", "recurring", "every", "alarm", "clean", "clear", "temp", "temporary",
    "screenshot", "clipboard", "recycle", "bin", "empty", "trash",
    "diagnostics", "system", "status", "battery", "charging",
    "processes", "optimize", "memory", "storage", "disk", "calendar", "time", "date",
    "desktop", "virtual", "switch", "jiggler", "awake", "sleep", "restart", "reboot", "shutdown",
    "open", "close", "launch", "terminate", "website", "settings", "application", "window", "active", "current",
    "minimize", "maximize",
    # Domain Engine keywords
    "email", "mail", "gmail", "outlook", "inbox", "attachment",
    "telegram", "spotify", "youtube", "yt", "search", "google",
    "code", "ide", "vscode", "antigravity", "terminal", "script",
    "vision", "capture", "display", "notify", "notification", "alert",
    "remember", "recall", "forget",
    # Core CLI control words
    "help", "commands", "exit", "quit",
    # Protected common action words & status states
    "deactivate", "disable", "activate", "enable", "stop", "start", "turn", "put", "set", "change", "adjust",
    "make", "allow", "let", "normal", "bring", "front", "focus"
]

def correct_spelling(query):
    if not query:
        return ""
    # Extract words (alphabetic sequences), numbers, and punctuation
    words = re.findall(r'[a-zA-Z]+|\d+|[^a-zA-Z\d]', query)
    corrected_words = []
    
    # Preserved target words/names that should never be corrected
    protected_targets = {
        "chrome", "notepad", "firefox", "edge", "cmd", "explorer", "calculator", "word", "excel", "powerpoint",
        "mummy", "mumm", "mumy", "dad", "john", "alex", "email", "mail", "gmail", "outlook", "telegram", "spotify",
        "youtube", "yt", "google", "screen", "take", "all", "and", "any", "set", "run", "get", "put", "off", "on", "out", "new", "now",
        "our", "one", "two", "ten", "day", "key", "say", "see", "what", "how", "who", "why", "can", "you", "not",
        "dont", "please", "sir", "back", "work", "time", "date", "gpt", "gravity", "chatgpt", "antigravity",
        "left", "right", "top", "bottom", "second", "seconds", "minute", "minutes", "hour", "hours", "after",
        "in", "at", "every", "arm", "armoury", "crate", "text", "msg", "send", "message"
    }

    for word in words:
        if word.isalpha() and len(word) >= 3:
            word_lower = word.lower()
            if word_lower in protected_targets:
                corrected_words.append(word)
                continue
            
            matches = difflib.get_close_matches(word_lower, KEYWORDS, n=1, cutoff=0.75)
            if matches:
                matched_kw = matches[0]
                if word.isupper():
                    corrected_words.append(matched_kw.upper())
                elif word[0].isupper():
                    corrected_words.append(matched_kw.capitalize())
                else:
                    corrected_words.append(matched_kw)
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)
            
    return "".join(corrected_words)

def translate_to_command(user_input):
    if not user_input:
        return ""
        
    # Translate common aliases/abbreviations
    user_input = re.sub(r'\bgpt\b', 'chatgpt', user_input, flags=re.IGNORECASE)
    user_input = re.sub(r'\bgravity\b', 'antigravity', user_input, flags=re.IGNORECASE)
    user_input = re.sub(r'\byt\b', 'youtube', user_input, flags=re.IGNORECASE)
        
    # Check if query matches a macro command directly before spell checking
    try:
        import os
        import json
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            macros = config.get("macros", {})
            
            clean_input = user_input.strip()
            clean_input_lower = clean_input.lower()
            
            for prefix in [
                "jarvis please don't ", "jarvis please ", "jarvis ", "hey jarvis ",
                "could you please ", "can you please ", "i want you to ", "please "
            ]:
                if clean_input_lower.startswith(prefix):
                    clean_input = clean_input[len(prefix):].strip()
                    clean_input_lower = clean_input.lower()
            
            macro_to_check = clean_input_lower
            for prefix in ["profile ", "activate ", "macro "]:
                if macro_to_check.startswith(prefix):
                    macro_to_check = macro_to_check[len(prefix):].strip()
            
            macro_to_check = re.sub(r'[\?\!\.\,]+$', '', macro_to_check).strip()
            
            if macro_to_check in macros:
                return user_input
    except Exception:
        pass

    # Apply fuzzy spelling correction to command keywords
    user_input = correct_spelling(user_input)
        
    query_clean = user_input.strip()
    query_lower = query_clean.lower()
    
    # Strip leading polite conversational phrases & filler prefixes
    prefixes_to_strip = [
        "jarvis please don't ", "jarvis please ", "jarvis ", "hey jarvis ",
        "could you please ", "can you please ", "can you help me to ",
        "i want you to ", "would you mind ", "kindly ", "please "
    ]
    for prefix in prefixes_to_strip:
        if query_lower.startswith(prefix):
            query_clean = query_clean[len(prefix):].strip()
            query_lower = query_clean.lower()

    # Strip trailing polite fillers iteratively
    changed = True
    while changed:
        old_len = len(query_clean)
        query_clean = re.sub(r'\s+(?:please|sir|jarvis|for me|right now|asap|ok)$', '', query_clean, flags=re.IGNORECASE).strip()
        query_lower = query_clean.lower()
        changed = (len(query_clean) != old_len)

    # --- SECTION 1: Deep Synonym Matrix Mapping ---
    synonyms = {
        # Keep Awake / Mouse Jiggler
        "keep awake": [
            "don't sleep", "dont sleep", "keep awake", "stay awake", 
            "no sleep", "start jiggler", "jiggle mouse", "stop screen sleep",
            "activate mouse jiggler", "keep computer awake", "dont let pc sleep",
            "activate jiggler", "enable jiggler", "turn on jiggler", "start keep awake"
        ],
        "stop awake": [
            "stop awake", "stop keep awake", "stop jiggling", "stop jiggler", 
            "let screen sleep", "allow sleep", "normal sleep", "deactivate mouse jiggler",
            "deactivate awake", "deactivate keep awake", "disable awake", "disable keep awake",
            "turn off awake", "turn off keep awake", "deactivate jiggler", "disable jiggler",
            "turn off jiggler"
        ],
        
        # System status / diagnostics
        "status": [
            "diagnostics", "system status", "hardware status", "pc status", 
            "how is my computer", "system diagnostics", "check diagnostics", "check system status",
            "how is my computer doing", "system diagnostics details", "pc state",
            "system check karo", "computer kesa chal raha hai"
        ],
        
        # Battery status
        "battery": [
            "battery", "battery level", "power status", "is my laptop charging", 
            "check battery percentage", "how much battery is left", "battery status",
            "charge kitna hai", "battery check", "battery dekho"
        ],
        
        # Lock screen
        "lock pc": [
            "lock screen", "lock windows", "lock pc", "lock workstation", 
            "secure computer", "lock my desktop", "lock the screen", "pc lock",
            "screen lock karo", "computer lock karo"
        ],
        
        # Sleep PC
        "sleep pc": [
            "put pc to sleep", "sleep pc", "standby mode", "put computer on standby",
            "sleep my computer", "put pc on sleep", "pc ko sula do"
        ],
        
        # Restart PC
        "restart pc": [
            "reboot pc", "restart computer", "reboot system", "restart windows",
            "restart my machine", "reboot the workstation", "system restart", "computer restart karo"
        ],
        
        # Shutdown PC
        "shutdown pc": [
            "turn off pc", "shutdown computer", "power off pc", "shutdown windows",
            "power off system", "turn off my computer", "pc band karo", "computer band karo"
        ],
        
        # Clean Temp
        "clean temp": [
            "clean temporary files", "clean temp", "delete temp", "clear cache", 
            "clear temp files", "clean temp folder", "clean temporary directory",
            "temp clean karo", "kachra saaf karo"
        ],
        
        # Empty Recycle Bin
        "empty trash": [
            "empty trash", "empty recycle bin", "clean recycle bin", "purge trash",
            "clear recycle bin", "empty the recycle bin", "bin empty", "clean bin",
            "trash saaf karo", "recycle bin khali karo"
        ],
        
        # Turn off screen
        "turn off screen": [
            "turn off monitor", "turn off screen", "display sleep", "sleep monitor",
            "turn off display", "put monitor to sleep", "screen band", "display band", "screen off",
            "screen band karo", "monitor band karo"
        ],
        
        # Dark / Light Theme
        "dark mode": [
            "enable dark mode", "turn on dark mode", "dark theme", "enable dark theme",
            "switch to dark mode", "switch to dark theme", "dark mode chalu karo"
        ],
        "light mode": [
            "enable light mode", "turn on light mode", "light theme", "enable light theme",
            "switch to light mode", "switch to light theme", "light mode chalu karo"
        ],
        
        # Top processes
        "top processes": [
            "top processes", "resource consumers", "what is eating my ram", 
            "check task manager", "high usage processes", "top resource hogs"
        ],
        
        # Idle time
        "idle time": [
            "idle time", "how long idle", "check idle duration", "inactive time",
            "how long have i been idle", "get system idle time"
        ],
        
        # Storage
        "disk check": [
            "disk check", "storage space", "check hard drive", "how much disk space is left", 
            "storage status", "disk space status", "check drive status", "check storage",
            "disk kitna khali hai"
        ],
        
        # RAM optimize
        "optimize memory": [
            "optimize memory", "trim ram", "free up ram", "clean ram", "boost memory",
            "free ram", "clean memory usage", "ram clear", "memory clear", "ram free karo"
        ],
        
        # Calendar
        "calendar": [
            "show calendar", "current month", "calendar view", "show me calendar", "calendar dekho"
        ],
        
        # Time / Date
        "time": [
            "what is the time", "check current time", "tell me time", "current time",
            "what time is it", "tell me the time", "time batao", "time please", "kitne baje hain"
        ],
        "date": [
            "what is today's date", "tell me date", "what date is today", "check date",
            "whats today's date", "tell me the date", "date batao", "what day today",
            "what is the day", "what day is it", "what's the day", "what day", "day is it", "aaj konsa din hai"
        ],
        
        # Screenshot
        "screenshot": [
            "take screenshot", "capture screen", "capture desktop", "take screen snap",
            "screenshot the screen", "capture my display", "ss", "click ss", "take ss",
            "ss click", "screenshot lo", "snap screen", "screen ka photo lo", "screenshot ka photo lo", "photo lo"
        ],
        
        # Clear Clipboard
        "clear clipboard": [
            "clear clipboard", "empty clipboard", "clear copy history", "empty the clipboard"
        ],
        
        # Desktop management
        "new desktop": ["new virtual desktop", "create desktop", "add virtual desktop"],
        "close desktop": ["close virtual desktop", "delete desktop", "remove virtual desktop"],
        "next desktop": ["next virtual desktop", "switch to next desktop"],
        "prev desktop": ["previous virtual desktop", "switch to previous desktop", "prev virtual desktop"],
        
        # Volume relative adjustment
        "volume up": ["increase volume", "volume up", "make it louder", "louder master", "raise master volume", "awaj badhao"],
        "volume down": ["decrease volume", "volume down", "make it quieter", "quieter master", "lower master volume", "awaj kam karo"],
        "mute master": ["mute audio", "mute pc", "silence master", "mute master volume", "mute master", "sound band", "speaker silent", "sound mute", "awaj band karo"],
        "unmute master": ["unmute audio", "unmute master", "restore sound", "unmute master volume", "sound chalu", "sound on", "unmute speaker", "awaj chalu karo"],
        
        # Playback controls
        "play": ["play song", "resume music", "resume playback", "start music", "play music", "gane chalu karo"],
        "pause": ["pause song", "stop music", "pause music", "pause playback", "gane rok do"],
        "next": ["skip track", "next song", "next track", "skip song", "agla gana"],
        "previous": ["previous track", "previous song", "prev song", "go back song", "pichla gana"],
        
        # Domain Engines Synonyms
        "whatsapp login": ["whatsapp login", "whatsapp scan qr", "login to whatsapp", "auth whatsapp", "open whatsapp", "launch whatsapp", "start whatsapp", "whatsapp open", "open wa", "whatsapp kholo", "whatsapp chalu karo"],
        "whatsapp unreads": ["check whatsapp unreads", "any unread whatsapp messages", "get whatsapp unreads", "whatsapp unread messages", "whatsapp unread dekho", "whatsapp unreads check"],
        "whatsapp logout": ["log out of whatsapp", "sign out of whatsapp", "whatsapp logout", "whatsapp signout", "whatsapp band karo"],
        "open youtube": ["open youtube", "launch youtube", "start youtube", "youtube open", "open yt"],
        "open settings": ["open settings", "show settings", "open system settings", "settings kholo"],
        "open wifi settings": ["open wifi settings", "wifi settings", "wifi settings kholo"],
        "open bluetooth settings": ["open bluetooth settings", "bluetooth settings", "bluetooth settings kholo"],
        "open display settings": ["open display settings", "display settings"],
        "open sound settings": ["open sound settings", "sound settings"],
        
        # Microphone controls
        "mute mic": ["mute microphone", "mute mic", "silence microphone", "mic band karo", "microphone band karo"],
        "unmute mic": ["unmute microphone", "unmute mic", "activate microphone", "mic chalu karo", "microphone chalu karo"],
        
        # Wifi signal details
        "wifi signal": ["wifi details", "wifi status", "wifi signal", "network details", "check wifi", "network status", "get ssid", "ssid info", "wifi connection"],
        
        # Close all programs
        "close all programs": [
            "close all the programs running", "close all programs", "close all running programs",
            "close all apps", "close all running apps", "close all open apps", "close all open programs",
            "terminate all programs", "terminate all apps", "kill all apps", "kill all programs",
            "close everything", "terminate everything",
            "sare apps band karo", "sare programs close karo", "sare apps close karo", "sare windows close karo"
        ]
    }
    
    # Check exact match in synonyms matrix after trimming punctuation
    clean_query_stripped = re.sub(r'[\?\!\.\,]+$', '', query_lower).strip()
    for cmd, patterns in synonyms.items():
        if clean_query_stripped in patterns:
            return cmd

    # --- SECTION 2: Dynamic Pattern Extraction & Hinglish Translation Rules ---
    
    # 1. Specific WhatsApp Mute / Unmute
    mute_match = re.match(r'^(?:whatsapp\s+)?(?:silence|mute)\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_lower)
    if mute_match:
        orig_match = re.match(r'^(?:whatsapp\s+)?(?:silence|mute)\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp mute "{orig_match.group(1).strip()}"'

    # 2. WhatsApp Direct Message (Explicit WhatsApp keyword)
    wa_explicit_msg = re.match(r'^(?:whatsapp\s+message\s+to|send\s+whatsapp\s+to|whatsapp\s+to)\s+([a-zA-Z0-9_\-\.\s]+?)\s+(?:text|message|saying)\s+(.+)$', query_lower)
    if wa_explicit_msg:
        orig_match = re.match(r'^(?:whatsapp\s+message\s+to|send\s+whatsapp\s+to|whatsapp\s+to)\s+([a-zA-Z0-9_\-\.\s]+?)\s+(?:text|message|saying)\s+(.+)$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp message to "{orig_match.group(1).strip()}" text "{orig_match.group(2).strip()}"'

    # 2.5 Send <message> to <contact> (e.g., send hello to dad / text happy birthday to alex)
    send_to_msg = re.match(r'^(?:send|message|text|msg)\s+(.+?)\s+to\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+)$', query_lower)
    if send_to_msg:
        orig_match = re.match(r'^(?:send|message|text|msg)\s+(.+?)\s+to\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+)$', query_clean, re.IGNORECASE)
        if orig_match:
            msg_content = orig_match.group(1).strip()
            contact_name = orig_match.group(2).strip()
            excluded_words = [
                "file", "document", "media", "image", "photo", "video", "pic", "picture", 
                "settings", "application", "macro", "schedule", "recurring", "mute", "unmute", "whatsapp",
                "switch", "focus", "bring", "open", "close", "run", "call", "video call",
                "email", "mail", "gmail", "outlook", "telegram"
            ]
            if contact_name.lower() not in excluded_words and msg_content.lower() not in excluded_words:
                return f'whatsapp message to "{contact_name}" text "{msg_content}"'

    # 3. Simple WhatsApp Send (Exclude other domain keywords)
    wa_simple_msg = re.match(r'^(?:message|text|msg|send)\s+([a-zA-Z0-9_\-\.\s]+?)\s+(.+)$', query_lower)
    if wa_simple_msg:
        orig_match = re.match(r'^(?:message|text|msg|send)\s+([a-zA-Z0-9_\-\.\s]+?)\s+(.+)$', query_clean, re.IGNORECASE)
        if orig_match:
            target = orig_match.group(1).strip()
            message = orig_match.group(2).strip()
            excluded_targets = [
                "file", "document", "media", "image", "photo", "video", "pic", "picture", 
                "settings", "application", "macro", "schedule", "recurring", "mute", "unmute", "whatsapp",
                "switch", "focus", "bring", "open", "close", "run", "call", "video call",
                "email", "mail", "gmail", "outlook", "telegram"
            ]
            if target.lower() not in excluded_targets:
                return f'whatsapp message to "{target}" text "{message}"'

    # 4. Settings Deep-Links
    settings_link = re.match(r'^(?:open|show)\s+([a-zA-Z0-9_\-\.\s]+?)\s+settings$', query_lower)
    if settings_link:
        setting_type = settings_link.group(1).strip()
        if setting_type in ["wifi", "bluetooth", "update", "sound", "display"]:
            return f'open {setting_type} settings'

    # 4.8 App Scheduling Normalization
    app_sched_rel = re.match(r'^(open|launch|start|run|kholo|chalu|close|kill|terminate|stop|band)\s+([a-zA-Z0-9_\-\.\s]+?)\s+(in|after)\s+(\d+)\s*(s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hr|hrs|hour|hours)$', query_lower)
    if app_sched_rel:
        action_verb = app_sched_rel.group(1).strip().lower()
        app_target = app_sched_rel.group(2).strip()
        delay_word = app_sched_rel.group(3).strip().lower()
        val_str = app_sched_rel.group(4).strip()
        unit_str = app_sched_rel.group(5).strip()
        
        if action_verb in ["close", "kill", "terminate", "stop", "band"]:
            act_type = "close"
        else:
            act_type = "open"
            
        if app_target.lower() not in ["pc", "computer", "system", "windows"]:
            return f'{act_type} {app_target} {delay_word} {val_str} {unit_str}'

    app_sched_abs = re.match(r'^(open|launch|start|run|kholo|chalu|close|kill|terminate|stop|band)\s+([a-zA-Z0-9_\-\.\s]+?)\s+at\s+(\d{1,2}:\d{2})$', query_lower)
    if app_sched_abs:
        action_verb = app_sched_abs.group(1).strip().lower()
        app_target = app_sched_abs.group(2).strip()
        time_str = app_sched_abs.group(3).strip()
        
        if action_verb in ["close", "kill", "terminate", "stop", "band"]:
            act_type = "close"
        else:
            act_type = "open"
            
        if app_target.lower() not in ["pc", "computer", "system", "windows"]:
            return f'{act_type} {app_target} at {time_str}'

    # 5. Hinglish Application Launch & Terminate
    app_launch_suff = re.match(r'^([a-zA-Z0-9_\-\.\s]+?)\s+(?:open|chalu\s+karo|start|chalu|kholo)$', query_lower)
    if app_launch_suff:
        orig_match = re.match(r'^([a-zA-Z0-9_\-\.\s]+?)\s+(?:open|chalu\s+karo|start|chalu|kholo)$', query_clean, re.IGNORECASE)
        if orig_match:
            app = orig_match.group(1).strip()
            if app.lower() not in ["pc", "computer", "system", "windows"]:
                return f'open {app}'

    app_launch = re.match(r'^(?:launch|start|open\s+application|run|open)\s+([a-zA-Z0-9_\-\.\s]+)$', query_lower)
    if app_launch:
        orig_match = re.match(r'^(?:launch|start|open\s+application|run|open)\s+([a-zA-Z0-9_\-\.\s]+)$', query_clean, re.IGNORECASE)
        if orig_match:
            app = orig_match.group(1).strip()
            if app.lower() not in ["pc", "computer", "system", "windows", "wifi settings", "bluetooth settings", "update settings", "sound settings", "display settings"]:
                return f'open {app}'

    # 6. Application Terminate (Colloquial & Hinglish)
    app_close_suff = re.match(r'^([a-zA-Z0-9_\-\.\s]+?)\s+(?:close|band\s+karo|stop|band)$', query_lower)
    if app_close_suff:
        orig_match = re.match(r'^([a-zA-Z0-9_\-\.\s]+?)\s+(?:close|band\s+karo|stop|band)$', query_clean, re.IGNORECASE)
        if orig_match:
            app = orig_match.group(1).strip()
            if app.lower() not in ["jiggler", "awake", "keep awake"]:
                return f'close {app}'

    app_close = re.match(r'^(?:kill|terminate|stop|shut|force\s+close|close)\s+([a-zA-Z0-9_\-\.\s]+)$', query_lower)
    if app_close:
        orig_match = re.match(r'^(?:kill|terminate|stop|shut|force\s+close|close)\s+([a-zA-Z0-9_\-\.\s]+)$', query_clean, re.IGNORECASE)
        if orig_match:
            app = orig_match.group(1).strip()
            if not app.isdigit() and app.lower() not in ["jiggler", "awake", "keep awake"]:
                return f'close {app}'

    # 6.8 Power scheduling normalization
    power_sched_rel = re.match(r'^(shutdown|turn\s+off|power\s+off|restart|reboot|sleep|put\s+to\s+sleep)(?:\s+(?:the\s+|my\s+)?(?:pc|computer|system|machine|desktop))?\s+(?:in|after)\s+(\d+)\s*(s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hr|hrs|hour|hours)$', query_lower)
    if power_sched_rel:
        raw_act = power_sched_rel.group(1).strip()
        val = power_sched_rel.group(2).strip()
        unit = power_sched_rel.group(3).strip()
        if raw_act in ["restart", "reboot"]:
            act_norm = "restart"
        elif raw_act in ["sleep", "put to sleep"]:
            act_norm = "sleep"
        else:
            act_norm = "shutdown"
        return f'{act_norm} pc in {val} {unit}'

    power_sched_abs = re.match(r'^(shutdown|turn\s+off|power\s+off|restart|reboot|sleep|put\s+to\s+sleep)(?:\s+(?:the\s+|my\s+)?(?:pc|computer|system|machine|desktop))?\s+at\s+(\d{1,2}:\d{2})$', query_lower)
    if power_sched_abs:
        raw_act = power_sched_abs.group(1).strip()
        time_val = power_sched_abs.group(2).strip()
        if raw_act in ["restart", "reboot"]:
            act_norm = "restart"
        elif raw_act in ["sleep", "put to sleep"]:
            act_norm = "sleep"
        else:
            act_norm = "shutdown"
        return f'{act_norm} pc at {time_val}'

    # 7. Persistent schedule commands translation
    sched_recurring = re.match(r'^schedule\s+(?:recurring\s+)?("?)(.+?)\1\s+every\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', query_lower)
    if sched_recurring:
        orig_match = re.match(r'^schedule\s+(?:recurring\s+)?("?)(.+?)\1\s+every\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', query_clean, re.IGNORECASE)
        if orig_match:
            cmd = orig_match.group(2).strip()
            val = orig_match.group(3).strip()
            unit = orig_match.group(4).strip()
            return f'schedule "{cmd}" every {val} {unit}'

    sched_relative = re.match(r'^schedule\s+("?)(.+?)\1\s+(?:in|after)\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', query_lower)
    if sched_relative:
        orig_match = re.match(r'^schedule\s+("?)(.+?)\1\s+(?:in|after)\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', query_clean, re.IGNORECASE)
        if orig_match:
            cmd = orig_match.group(2).strip()
            val = orig_match.group(3).strip()
            unit = orig_match.group(4).strip()
            return f'schedule "{cmd}" in {val} {unit}'

    sched_absolute = re.match(r'^schedule\s+("?)(.+?)\1\s+at\s+(\d{1,2}:\d{2})$', query_lower)
    if sched_absolute:
        orig_match = re.match(r'^schedule\s+("?)(.+?)\1\s+at\s+(\d{1,2}:\d{2})$', query_clean, re.IGNORECASE)
        if orig_match:
            cmd = orig_match.group(2).strip()
            time_val = orig_match.group(3).strip()
            return f'schedule "{cmd}" at {time_val}'

    return query_clean
