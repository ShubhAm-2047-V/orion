"""
Multilingual Text Normalizer & Preprocessor.
Supports English, Hindi, Marathi, and Hinglish with colloquial slang, fillers, and phonetic spelling variants.
"""
import re
import unicodedata
from typing import Tuple, Dict

# Conversational fillers in English, Hindi, Hinglish, Marathi
CONVERSATIONAL_FILLERS = [
    # English fillers & polite prefixes
    r"\b(hey|hello|hi|dear)?\s*(jarvis|orion|alexa|siri|computer|bot)\b",
    r"\b(could|can|would)\s+you\s+(please\s+)?(help\s+me\s+to\s+)?",
    r"\b(i\s+want\s+you\s+to|please|kindly|just|do\s+one\s+thing)\b",
    # Hindi / Hinglish fillers
    r"\b(bhai|yaar|are|sun|suno|bhaiya|boss|dost)\b",
    r"\b(mere|meri|apne|apna|mera)\s+(laptop|computer|pc|system)?\s*(ka|ki|ke|me|pe)?\b",
    r"\b(kripya|zara|ek\s+kaam\s+karo|jaldi\s+se|turant)\b",
    # Marathi fillers
    r"\b(bhava|dada|re|bhau|mitra)\b",
    r"\b(majhya|aamchya|majha)\s+(laptop|computer|pc|system)?\s*(cha|chi|che|madhe)?\b",
    r"\b(krupaya|lavkar|thoda|zara)\b"
]

# Multilingual action keyword maps
ACTION_MAPPINGS = {
    # Open / Launch
    "open": [
        "khol de", "khol do", "kholo", "khol", "chalu karo", "chalu kar do", "shuru karo", "launch karo", "start karo",
        "ugad", "ugada", "chalu kara", "shuru kara", "arambh kara", "suru kara", "start kara"
    ],
    # Close / Terminate
    "close": [
        "band karo", "band kar do", "hatao", "rok do", "khatam karo",
        "band kara", "thambva", "thamba", "thambav"
    ],
    # Search
    "search": [
        "dhoondho", "khojo", "search karo", "dhundo", "pata karo",
        "shodha", "shodh", "mahit karaan"
    ],
    # Clean / Empty
    "clean": [
        "saaf karo", "saaf kar do", "khali karo", "delete karo", "hata do",
        "swachh kara", "saf kara", "rikami kara"
    ],
    # Volume Increase / Decrease
    "volume_up": [
        "aawaz badhao", "volume badhao", "aawaz tez karo", "sound badhao",
        "aawaz vadhva", "sound vadhva"
    ],
    "volume_down": [
        "aawaz kam karo", "volume kam karo", "aawaz dheemi karo", "sound kam karo",
        "aawaz kami kara", "sound kami kara"
    ],
    # Lock / Sleep
    "lock": [
        "lock karo", "lock kar do", "bandh karo pc", "lock kara"
    ],
    "sleep": [
        "sula do", "sleep mode me dalo", "sleep karo", "zopva"
    ]
}

# Common phonetic typo correction map
TYPO_CORRECTIONS = {
    "chorme": "chrome", "chrom": "chrome", "gogle": "google", "googl": "google",
    "calc": "calculator", "calcy": "calculator", "calculater": "calculator", "kalkulator": "calculator",
    "notpad": "notepad", "notepd": "notepad",
    "yt": "youtube", "utube": "youtube", "you tube": "youtube",
    "watsapp": "whatsapp", "whats app": "whatsapp", "whatsap": "whatsapp", "watsap": "whatsapp",
    "volum": "volume", "sounde": "sound", "scrren": "screen", "scrin": "screen",
    "shut down": "shutdown", "re boot": "reboot", "re start": "restart",
    "foler": "folder", "floder": "folder", "fldr": "folder", "directry": "directory",
    "pyton": "python", "pyhton": "python", "py": "python"
}

def detect_language(text: str) -> str:
    """
    Detects language: English (en), Hindi (hi), Marathi (mr), or Hinglish.
    """
    text_lower = text.lower()
    
    # Devanagari script detection
    has_devanagari = any('\u0900' <= char <= '\u097F' for char in text)
    if has_devanagari:
        # Check specific Marathi characters or words
        marathi_markers = ["आहे", "करा", "चालू", "उघडा", "बंद", "माझ्या", "लवकर", "थोडं", "भावा", "कसा"]
        if any(marker in text for marker in marathi_markers):
            return "mr"
        return "hi"
        
    # Romanized Marathi markers
    marathi_roman = ["kara", "ugada", "vadhva", "kami kara", "thambva", "majhya", "bhava", "kasa", "ahe", "karun", "dya"]
    if any(re.search(r'\b' + re.escape(w) + r'\b', text_lower) for w in marathi_roman):
        return "mr"

    # Romanized Hindi markers (Hinglish)
    hindi_roman = [
        "khol", "kholo", "khol de", "khol do", "chalu", "karo", "kar do", "band", "saaf", 
        "badhao", "badha", "sula", "dhoondho", "dhundo", "dikhao", "batao", "bhai", 
        "mera", "mere", "meri", "kripya", "zara", "hatao", "rakho", "bana", "banao"
    ]
    if any(re.search(r'\b' + re.escape(w) + r'\b', text_lower) for w in hindi_roman):
        return "hinglish"
        
    return "en"

def normalize_text(text: str) -> Tuple[str, str, Dict[str, str]]:
    """
    Normalizes human language input into a clean, canonical form.
    Returns (cleaned_text, detected_language, metadata).
    """
    if not text:
        return "", "en", {}

    # Strip unicode accents / normalize characters
    text = unicodedata.normalize('NFKD', text)
    
    # Detect language before stripping slang markers
    detected_lang = detect_language(text)
    
    # Lowercase for canonical processing
    cleaned = text.lower().strip()
    
    # Typo correction for common words
    for typo, correction in TYPO_CORRECTIONS.items():
        cleaned = re.sub(r'\b' + re.escape(typo) + r'\b', correction, cleaned)

    # Remove conversational fillers & polite phrases
    for filler_regex in CONVERSATIONAL_FILLERS:
        cleaned = re.sub(filler_regex, "", cleaned, flags=re.IGNORECASE)

    # Clean multiple spaces & trailing punctuation
    cleaned = re.sub(r'[!?.,;:]+$', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Normalize multilingual verb phrases into standardized command intents
    # Example: "calculator khol de" -> "open calculator"
    for action, phrases in ACTION_MAPPINGS.items():
        for phrase in phrases:
            # Pattern: <target> <phrase> (e.g., "calculator khol de")
            match_suffix = re.search(r'^(.*?)\s+' + re.escape(phrase) + r'$', cleaned)
            if match_suffix:
                target = match_suffix.group(1).strip()
                if action == "open":
                    cleaned = f"open {target}"
                elif action == "close":
                    cleaned = f"close {target}"
                elif action == "search":
                    cleaned = f"search {target}"
                elif action == "clean":
                    cleaned = f"clean {target}"
                elif action == "volume_up":
                    cleaned = f"volume up {target}".strip()
                elif action == "volume_down":
                    cleaned = f"volume down {target}".strip()
                elif action == "lock":
                    cleaned = "lock pc"
                elif action == "sleep":
                    cleaned = "sleep pc"
                break
                
            # Pattern: <phrase> <target> (e.g., "khol de calculator")
            match_prefix = re.search(r'^' + re.escape(phrase) + r'\s+(.*?)$', cleaned)
            if match_prefix:
                target = match_prefix.group(1).strip()
                if action == "open":
                    cleaned = f"open {target}"
                elif action == "close":
                    cleaned = f"close {target}"
                elif action == "search":
                    cleaned = f"search {target}"
                elif action == "clean":
                    cleaned = f"clean {target}"
                elif action == "volume_up":
                    cleaned = f"volume up {target}".strip()
                elif action == "volume_down":
                    cleaned = f"volume down {target}".strip()
                elif action == "lock":
                    cleaned = "lock pc"
                elif action == "sleep":
                    cleaned = "sleep pc"
                break

    # Final cleanup
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    metadata = {
        "original_length": len(text),
        "normalized_length": len(cleaned),
        "language": detected_lang
    }
    
    return cleaned, detected_lang, metadata
