import re
import difflib

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
    
    for word in words:
        if word.isalpha() and len(word) >= 3:
            word_lower = word.lower()
            # Do not correct common contact names/app names or common words that might resemble keywords
            if word_lower in ["chrome", "notepad", "firefox", "edge", "cmd", "explorer", "calculator", "word", "excel", "powerpoint", "mummy", "mumm", "mumy", "all", "and", "any", "set", "run", "get", "put", "off", "on", "out", "new", "now", "our", "one", "two", "ten", "day", "key", "say", "see", "what", "how", "who", "why", "can", "you", "not", "dont", "please", "sir", "back", "work", "time", "date", "gpt", "gravity", "chatgpt", "antigravity", "left", "right", "top", "bottom", "second", "seconds", "minute", "minutes", "hour", "hours", "after", "in", "at", "every"]:
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
        
    # Translate aliases/abbreviations as whole words
    user_input = re.sub(r'\bgpt\b', 'chatgpt', user_input, flags=re.IGNORECASE)
    user_input = re.sub(r'\bgravity\b', 'antigravity', user_input, flags=re.IGNORECASE)
        
    # Check if the query matches a macro command exactly before spell checking
    try:
        import os
        import json
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            macros = config.get("macros", {})
            
            clean_input = user_input.strip()
            clean_input_lower = clean_input.lower()
            
            for prefix in ["jarvis please don't ", "jarvis please ", "jarvis ", "hey jarvis ", "please "]:
                if clean_input_lower.startswith(prefix):
                    clean_input = clean_input[len(prefix):].strip()
                    clean_input_lower = clean_input.lower()
            
            macro_to_check = clean_input_lower
            for prefix in ["profile ", "activate ", "macro "]:
                if macro_to_check.startswith(prefix):
                    macro_to_check = macro_to_check[len(prefix):].strip()
            
            macro_to_check = re.sub(r'[\?\!\.\,]+$', '', macro_to_check).strip()
            
            if macro_to_check in macros:
                return user_input  # Return immediately as-is
    except Exception:
        pass

    # Apply fuzzy spelling correction to command keywords
    user_input = correct_spelling(user_input)
        
    query_clean = user_input.strip()
    query_lower = query_clean.lower()
    
    # Remove leading common conversational phrases
    # e.g., "jarvis please don't sleep" -> "don't sleep"
    for prefix in ["jarvis please ", "jarvis ", "hey jarvis ", "please "]:
        if query_lower.startswith(prefix):
            query_clean = query_clean[len(prefix):].strip()
            query_lower = query_clean.lower()
            
    # --- SECTION 1: Exact Synonyms / Keyword Matches ---
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
            "how is my computer", "system diagnostics", "check diagnostics",
            "how is my computer doing", "system diagnostics details", "pc state"
        ],
        
        # Battery status
        "battery": [
            "battery", "battery level", "power status", "is my laptop charging", 
            "check battery percentage", "how much battery is left", "battery status",
            "charge kitna hai", "battery check"
        ],
        
        # Lock screen
        "lock pc": [
            "lock screen", "lock windows", "lock pc", "lock workstation", 
            "secure computer", "lock my desktop", "lock the screen", "pc lock"
        ],
        
        # Sleep PC
        "sleep pc": [
            "put pc to sleep", "sleep pc", "standby mode", "put computer on standby",
            "sleep my computer", "put pc on sleep"
        ],
        
        # Restart PC
        "restart pc": [
            "reboot pc", "restart computer", "reboot system", "restart windows",
            "restart my machine", "reboot the workstation", "system restart"
        ],
        
        # Shutdown PC
        "shutdown pc": [
            "turn off pc", "shutdown computer", "power off pc", "shutdown windows",
            "power off system", "turn off my computer"
        ],
        
        # Clean Temp
        "clean temp": [
            "clean temporary files", "clean temp", "delete temp", "clear cache", 
            "clear temp files", "clean temp folder", "clean temporary directory"
        ],
        
        # Empty Recycle Bin
        "empty trash": [
            "empty trash", "empty recycle bin", "clean recycle bin", "purge trash",
            "clear recycle bin", "empty the recycle bin", "bin empty", "clean bin"
        ],
        
        # Turn off screen
        "turn off screen": [
            "turn off monitor", "turn off screen", "display sleep", "sleep monitor",
            "turn off display", "put monitor to sleep", "screen band", "display band", "screen off"
        ],
        
        # Dark / Light Theme
        "dark mode": [
            "enable dark mode", "turn on dark mode", "dark theme", "enable dark theme",
            "switch to dark mode", "switch to dark theme"
        ],
        "light mode": [
            "enable light mode", "turn on light mode", "light theme", "enable light theme",
            "switch to light mode", "switch to light theme"
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
            "storage status", "disk space status", "check drive status", "check storage"
        ],
        
        # RAM optimize
        "optimize memory": [
            "optimize memory", "trim ram", "free up ram", "clean ram", "boost memory",
            "free ram", "clean memory usage", "ram clear", "memory clear"
        ],
        
        # Calendar
        "calendar": [
            "show calendar", "current month", "calendar view", "show me calendar"
        ],
        
        # Time / Date
        "time": [
            "what is the time", "check current time", "tell me time", "current time",
            "what time is it", "tell me the time", "time batao", "time please"
        ],
        "date": [
            "what is today's date", "tell me date", "what date is today", "check date",
            "whats today's date", "tell me the date", "date batao", "what day today"
        ],
        
        # Screenshot (colloquial "ss")
        "screenshot": [
            "take screenshot", "capture screen", "capture desktop", "take screen snap",
            "screenshot the screen", "capture my display", "ss", "click ss", "take ss",
            "ss click", "screenshot lo", "snap screen"
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
        "volume up": ["increase volume", "volume up", "make it louder", "louder master", "raise master volume"],
        "volume down": ["decrease volume", "volume down", "make it quieter", "quieter master", "lower master volume"],
        "mute master": ["mute audio", "mute pc", "silence master", "mute master volume", "mute master", "sound band", "speaker silent", "sound mute"],
        "unmute master": ["unmute audio", "unmute master", "restore sound", "unmute master volume", "sound chalu", "sound on", "unmute speaker"],
        
        # Playback controls
        "play": ["play song", "resume music", "resume playback", "start music", "play music"],
        "pause": ["pause song", "stop music", "pause music", "pause playback"],
        "next": ["skip track", "next song", "next track", "skip song"],
        "previous": ["previous track", "previous song", "prev song", "go back song"],
        
        # WhatsApp General commands
        "whatsapp login": ["whatsapp login", "whatsapp scan qr", "login to whatsapp", "auth whatsapp"],
        "whatsapp unreads": ["check whatsapp unreads", "any unread whatsapp messages", "get whatsapp unreads", "whatsapp unread messages", "whatsapp unread dekho", "whatsapp unreads check"],
        "whatsapp logout": ["log out of whatsapp", "sign out of whatsapp", "whatsapp logout", "whatsapp signout", "whatsapp band karo"],
        
        # Microphone controls
        "mute mic": ["mute microphone", "mute mic", "silence microphone", "mic band karo", "microphone band karo"],
        "unmute mic": ["unmute microphone", "unmute mic", "activate microphone", "mic chalu karo", "microphone chalu karo"],
        
        # Wifi signal details
        "wifi signal": ["wifi details", "wifi status", "wifi signal", "network details", "check wifi", "network status", "get ssid", "ssid info", "wifi connection"]
    }
    
    # Loop over synonym lists to find a direct match
    # Strip any trailing punctuation (like '?') to handle "what is the time?"
    clean_query_stripped = re.sub(r'[\?\!\.\,]+$', '', query_lower).strip()
    for cmd, patterns in synonyms.items():
        if clean_query_stripped in patterns:
            return cmd
            
    # --- SECTION 2: Regex Extraction and Translations ---
    
    # PRECEDENCE RULE: Check specific action intents (mute, calls, status, files) before generic messages
    
    # 1. WhatsApp Mute / Unmute
    mute_match = re.match(r'^(?:whatsapp\s+)?(?:silence|mute)\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_lower)
    if mute_match:
        orig_match = re.match(r'^(?:whatsapp\s+)?(?:silence|mute)\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp mute "{orig_match.group(1).strip()}"'
            
    unmute_match = re.match(r'^(?:whatsapp\s+)?unmute\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_lower)
    if unmute_match:
        orig_match = re.match(r'^(?:whatsapp\s+)?unmute\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp unmute "{orig_match.group(1).strip()}"'

    # 2. WhatsApp Read Last (English and Hinglish)
    read_last_match = re.match(r'^(?:whatsapp\s+)?(?:read|check|get)\s+last\s+(?:message|text|msg)?\s*(?:from|of)\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_lower)
    if read_last_match:
        orig_match = re.match(r'^(?:whatsapp\s+)?(?:read|check|get)\s+last\s+(?:message|text|msg)?\s*(?:from|of)\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp read last from "{orig_match.group(1).strip()}"'

    hinglish_read = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+ka\s+(?:last\s+)?(?:message|msg|text)\s*(?:read\s+karo|padho|dekho)?$', query_lower)
    if hinglish_read:
        orig_match = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+ka\s+(?:last\s+)?(?:message|msg|text)\s*(?:read\s+karo|padho|dekho)?$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp read last from "{orig_match.group(1).strip()}"'

    # 3. WhatsApp Status / Online check (English and Hinglish)
    status_match = re.match(r'^(?:whatsapp\s+)?(?:check\s+)?(?:online\s+)?status\s+(?:of|for)\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_lower)
    if status_match:
        orig_match = re.match(r'^(?:whatsapp\s+)?(?:check\s+)?(?:online\s+)?status\s+(?:of|for)\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp status of "{orig_match.group(1).strip()}"'

    hinglish_status = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+(?:online\s+hai\s+kya|ka\s+status\s+check\s+karo|status|online\s+status)$', query_lower)
    if hinglish_status:
        orig_match = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+(?:online\s+hai\s+kya|ka\s+status\s+check\s+karo|status|online\s+status)$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp status of "{orig_match.group(1).strip()}"'

    # 4. WhatsApp Call / Video Call (English and Hinglish)
    video_call_match = re.match(r'^(?:whatsapp\s+)?(?:make\s+a\s+)?video\s+call\s+(?:to\s+)?([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_lower)
    if video_call_match:
        orig_match = re.match(r'^(?:whatsapp\s+)?(?:make\s+a\s+)?video\s+call\s+(?:to\s+)?([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp video call "{orig_match.group(1).strip()}"'

    voice_call_match = re.match(r'^(?:whatsapp\s+)?(?:make\s+a\s+)?(?:voice\s+)?call\s+(?:to\s+)?([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_lower)
    if voice_call_match:
        orig_match = re.match(r'^(?:whatsapp\s+)?(?:make\s+a\s+)?(?:voice\s+)?call\s+(?:to\s+)?([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp call "{orig_match.group(1).strip()}"'

    hinglish_call = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+ko\s+(?:whatsapp\s+)?(?:voice\s+)?call\s+(?:karo|lagao|karna)(?:\s+on\s+whatsapp)?$', query_lower)
    if hinglish_call:
        orig_match = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+ko\s+(?:whatsapp\s+)?(?:voice\s+)?call\s+(?:karo|lagao|karna)(?:\s+on\s+whatsapp)?$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp call "{orig_match.group(1).strip()}"'

    hinglish_vcall = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+ko\s+(?:whatsapp\s+)?video\s+call\s+(?:karo|lagao)(?:\s+on\s+whatsapp)?$', query_lower)
    if hinglish_vcall:
        orig_match = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+ko\s+(?:whatsapp\s+)?video\s+call\s+(?:karo|lagao)(?:\s+on\s+whatsapp)?$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'whatsapp video call "{orig_match.group(1).strip()}"'

    # 5. WhatsApp Send File (English and Hinglish)
    send_file_match = re.match(r'^(?:whatsapp\s+)?(?:send|upload)\s+(?:a|an|the\s+)?(?:file|document|media|image|photo|video)\s+to\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?(?:\s+path\s+(.+))?$', query_lower)
    if send_file_match:
        orig_match = re.match(r'^(?:whatsapp\s+)?(?:send|upload)\s+(?:a|an|the\s+)?(?:file|document|media|image|photo|video)\s+to\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)(?:\s+on\s+whatsapp)?(?:\s+path\s+(.+))?$', query_clean, re.IGNORECASE)
        if orig_match:
            target = orig_match.group(1).strip()
            path = orig_match.group(2).strip() if orig_match.group(2) else None
            if path:
                return f'whatsapp send file to "{target}" path "{path}"'
            return f'whatsapp send file to "{target}"'

    hinglish_file = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+ko\s+(?:a|an|the\s+)?(?:file|document|media|image|photo|video|pic|picture)\s+(?:send\s+)?(?:bhejo|karo)(?:\s+path\s+(.+))?$', query_lower)
    if hinglish_file:
        orig_match = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+ko\s+(?:a|an|the\s+)?(?:file|document|media|image|photo|video|pic|picture)\s+(?:send\s+)?(?:bhejo|karo)(?:\s+path\s+(.+))?$', query_clean, re.IGNORECASE)
        if orig_match:
            target = orig_match.group(1).strip()
            path = orig_match.group(2).strip() if orig_match.group(2) else None
            if path:
                return f'whatsapp send file to "{target}" path "{path}"'
            return f'whatsapp send file to "{target}"'

    # 6. WhatsApp Broadcast
    wa_broadcast = re.match(r'^(?:whatsapp\s+)?broadcast\s+(?:message\s+)?to\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF\,]+?)\s+(?:saying|text|message|msg)\s+(.+)$', query_lower)
    if wa_broadcast:
        orig_match = re.match(r'^(?:whatsapp\s+)?broadcast\s+(?:message\s+)?to\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF\,]+?)\s+(?:saying|text|message|msg)\s+(.+)$', query_clean, re.IGNORECASE)
        if orig_match:
            targets = orig_match.group(1).strip()
            message = orig_match.group(2).strip()
            return f'whatsapp broadcast to "{targets}" text "{message}"'

    # 12. Display Brightness (e.g. set brightness 50, screen brightness 80, set screen brightness to 0)
    brightness_set = re.match(r'^(?:set\s+|change\s+|adjust\s+)?(?:screen\s+)?brightness(?:\s+level)?(?:\s+to)?\s+(\d+)(?:\s*%)?$', query_lower)
    if brightness_set:
        return f'brightness {brightness_set.group(1)}'

    # 13. Domain / Website Open (e.g. open youtube.com, go to google.com, visit github.com)
    domain_open = re.match(r'^(?:open|launch|website|go\s+to|visit)\s+([a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,6})$', query_lower)
    if domain_open:
        orig_match = re.match(r'^(?:open|launch|website|go\s+to|visit)\s+([a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,6})$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'website {orig_match.group(1).strip()}'

    # 14. Focus / Bring App to Front (e.g. bring chrome to front, focus on notepad, switch focus to word)
    focus_match = re.match(r'^(?:bring\s+(.+?)\s+(?:to\s+)?front|bring\s+to\s+front\s+(.+?)|focus\s+on\s+(.+?)|switch\s+focus\s+to\s+(.+?))$', query_lower)
    if focus_match:
        target_app = None
        for group_val in focus_match.groups():
            if group_val:
                target_app = group_val.strip()
                break
        if target_app:
            orig_match = re.match(r'^(?:bring\s+(.+?)\s+(?:to\s+)?front|bring\s+to\s+front\s+(.+?)|focus\s+on\s+(.+?)|switch\s+focus\s+to\s+(.+?))$', query_clean, re.IGNORECASE)
            if orig_match:
                for orig_val in orig_match.groups():
                    if orig_val:
                        target_app = orig_val.strip()
                        break
            return f'switch to {target_app}'

    # 7. WhatsApp Generic Messages (evaluated LAST to prevent greedy overlap)
    # Pattern A: "send message to Mummy saying hello"
    wa_msg_saying = re.match(r'^(?:send\s+(?:a\s+)?)?(?:whatsapp\s+)?(?:message|text|msg)?\s*(?:to\s+)?([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+(?:saying|text|message|msg)\s+(.+)$', query_lower)
    if wa_msg_saying:
        orig_match = re.match(r'^(?:send\s+(?:a\s+)?)?(?:whatsapp\s+)?(?:message|text|msg)?\s*(?:to\s+)?([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+(?:saying|text|message|msg)\s+(.+)$', query_clean, re.IGNORECASE)
        if orig_match:
            target = orig_match.group(1).strip()
            message = orig_match.group(2).strip()
            if target.lower().endswith(" on whatsapp"):
                target = target[:-12].strip()
            return f'whatsapp message to "{target}" text "{message}"'

    # Pattern B: "send hello to Mummy"
    has_msg_prefix = re.match(r'^(?:send|message|text|msg)\b', query_lower) is not None
    has_msg_suffix = re.search(r'(?:on\s+whatsapp|via\s+whatsapp)$', query_lower) is not None
    wa_msg_to = None
    if has_msg_prefix or has_msg_suffix:
        wa_msg_to = re.match(r'^(?:send\s+)?(?:a\s+)?(?:message|text|msg)?\s*("?)(.+?)\1\s+to\s+("?)([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\3(?:\s+on\s+whatsapp|\s+via\s+whatsapp)?$', query_lower)
    if wa_msg_to:
        orig_match = re.match(r'^(?:send\s+)?(?:a\s+)?(?:message|text|msg)?\s*("?)(.+?)\1\s+to\s+("?)([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\3(?:\s+on\s+whatsapp|\s+via\s+whatsapp)?$', query_clean, re.IGNORECASE)
        if orig_match:
            message = orig_match.group(2).strip()
            target = orig_match.group(4).strip()
            if target.lower().endswith(" on whatsapp"):
                target = target[:-12].strip()
            excluded_verbs = [
                "file", "document", "media", "image", "photo", "video", "a file", "a document", "a media", 
                "an image", "a photo", "a video", "pic", "a pic", "picture", "a picture",
                "switch", "focus", "bring", "open", "close", "run", "call", "video call", "mute", "unmute", 
                "set", "change", "adjust", "play", "pause", "skip", "go", "show"
            ]
            if message.lower() not in excluded_verbs:
                return f'whatsapp message to "{target}" text "{message}"'

    # Pattern C: Hinglish Message: Mummy ko message karo hello
    wa_hinglish_msg = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+ko\s+(?:message|text|msg|bhejo|karo)\s+(?:karo|bhejo\s+)?(.+)$', query_lower)
    if wa_hinglish_msg:
        orig_match = re.match(r'^([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+ko\s+(?:message|text|msg|bhejo|karo)\s+(?:karo|bhejo\s+)?(.+)$', query_clean, re.IGNORECASE)
        if orig_match:
            target = orig_match.group(1).strip()
            message = orig_match.group(2).strip()
            return f'whatsapp message to "{target}" text "{message}"'

    # Pattern D: Simple Send: message Mummy hello / text Dad call me / send Mummy hi
    wa_simple_msg = re.match(r'^(?:message|text|msg|send)\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+(.+)$', query_lower)
    if wa_simple_msg:
        orig_match = re.match(r'^(?:message|text|msg|send)\s+([a-zA-Z0-9_\-\.\s\u00C0-\u017F\u2600-\u27BF]+?)\s+(.+)$', query_clean, re.IGNORECASE)
        if orig_match:
            target = orig_match.group(1).strip()
            message = orig_match.group(2).strip()
            excluded_targets = [
                "file", "document", "media", "image", "photo", "video", "pic", "picture", 
                "settings", "application", "macro", "schedule", "recurring", "mute", "unmute", "whatsapp",
                "switch", "focus", "bring", "open", "close", "run", "call", "video call"
            ]
            if target.lower() not in excluded_targets:
                return f'whatsapp message to "{target}" text "{message}"'

    # 8. Settings Deep-Links
    settings_link = re.match(r'^(?:open|show)\s+([a-zA-Z0-9_\-\.\s]+?)\s+settings$', query_lower)
    if settings_link:
        setting_type = settings_link.group(1).strip()
        if setting_type in ["wifi", "bluetooth", "update", "sound", "display"]:
            return f'open {setting_type} settings'

    # 9. Volume Set (Master and App-Specific)
    vol_master_set = re.match(r'^(?:set\s+)?(?:master\s+)?volume\s+(?:to\s+)?(\d+)$', query_lower)
    if vol_master_set:
        return f'volume master {vol_master_set.group(1)}'
        
    vol_app_set = re.match(r'^(?:set\s+)?volume\s+(?:of|for)\s+([a-zA-Z0-9_\-\.\s]+?)\s+(?:to\s+)?(\d+)$', query_lower)
    if vol_app_set:
        orig_match = re.match(r'^(?:set\s+)?volume\s+(?:of|for)\s+([a-zA-Z0-9_\-\.\s]+?)\s+(?:to\s+)?(\d+)$', query_clean, re.IGNORECASE)
        if orig_match:
            return f'volume {orig_match.group(1).strip()} {orig_match.group(2).strip()}'
            
    vol_app_mute = re.match(r'^mute\s+([a-zA-Z0-9_\-\.\s]+?)$', query_lower)
    if vol_app_mute:
        orig_match = re.match(r'^mute\s+([a-zA-Z0-9_\-\.\s]+?)$', query_clean, re.IGNORECASE)
        if orig_match:
            app = orig_match.group(1).strip()
            if app.lower() not in ["master", "pc", "system", "speakers", "speaker", "audio", "mic", "microphone"]:
                return f'mute {app}'
                
    vol_app_unmute = re.match(r'^unmute\s+([a-zA-Z0-9_\-\.\s]+?)$', query_lower)
    if vol_app_unmute:
        orig_match = re.match(r'^unmute\s+([a-zA-Z0-9_\-\.\s]+?)$', query_clean, re.IGNORECASE)
        if orig_match:
            app = orig_match.group(1).strip()
            if app.lower() not in ["master", "pc", "system", "speakers", "speaker", "audio", "mic", "microphone"]:
                return f'unmute {app}'

    # 10. Windows Applications launch and terminate (Colloquial formats)
    # Pattern A: chrome open / chrome chalu karo
    app_launch_suff = re.match(r'^([a-zA-Z0-9_\-\.\s]+?)\s+(?:open|chalu\s+karo|start|chalu)$', query_lower)
    if app_launch_suff:
        orig_match = re.match(r'^([a-zA-Z0-9_\-\.\s]+?)\s+(?:open|chalu\s+karo|start|chalu)$', query_clean, re.IGNORECASE)
        if orig_match:
            app = orig_match.group(1).strip()
            if app.lower() not in ["pc", "computer", "system", "windows"]:
                return f'open {app}'

    # Pattern B: open chrome
    app_launch = re.match(r'^(?:launch|start|open\s+application|run)\s+([a-zA-Z0-9_\-\.\s]+)$', query_lower)
    if app_launch:
        orig_match = re.match(r'^(?:launch|start|open\s+application|run)\s+([a-zA-Z0-9_\-\.\s]+)$', query_clean, re.IGNORECASE)
        if orig_match:
            app = orig_match.group(1).strip()
            if app.lower() not in ["pc", "computer", "system", "windows", "wifi settings", "bluetooth settings", "update settings", "sound settings", "display settings"]:
                return f'open {app}'
                
    # Pattern A: chrome close / chrome band karo
    app_close_suff = re.match(r'^([a-zA-Z0-9_\-\.\s]+?)\s+(?:close|band\s+karo|stop|band)$', query_lower)
    if app_close_suff:
        orig_match = re.match(r'^([a-zA-Z0-9_\-\.\s]+?)\s+(?:close|band\s+karo|stop|band)$', query_clean, re.IGNORECASE)
        if orig_match:
            app = orig_match.group(1).strip()
            if app.lower() not in ["jiggler", "awake", "keep awake"]:
                return f'close {app}'

    # Pattern B: close chrome
    app_close = re.match(r'^(?:kill|terminate|stop|shut|force\s+close)\s+([a-zA-Z0-9_\-\.\s]+)$', query_lower)
    if app_close:
        orig_match = re.match(r'^(?:kill|terminate|stop|shut|force\s+close)\s+([a-zA-Z0-9_\-\.\s]+)$', query_clean, re.IGNORECASE)
        if orig_match:
            app = orig_match.group(1).strip()
            if not app.isdigit() and app.lower() not in ["jiggler", "awake", "keep awake"]:
                return f'close {app}'

    # 11. Persistent schedule commands translation
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

    sched_date = re.match(r'^schedule\s+("?)(.+?)\1\s+on\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+at\s+(\d{1,2}:\d{2})$', query_lower)
    if sched_date:
        orig_match = re.match(r'^schedule\s+("?)(.+?)\1\s+on\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+at\s+(\d{1,2}:\d{2})$', query_clean, re.IGNORECASE)
        if orig_match:
            cmd = orig_match.group(2).strip()
            date_val = orig_match.group(3).strip()
            time_val = orig_match.group(4).strip()
            return f'schedule "{cmd}" on {date_val} at {time_val}'

    return user_input
