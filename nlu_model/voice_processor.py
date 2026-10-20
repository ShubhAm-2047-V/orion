"""
Voice Input & Speech Recognition Engine.
Handles microphone recording, noise calibration, multi-language recognition (en-IN, hi-IN, mr-IN),
and error recovery for conversational voice commands.
"""
import time
from typing import Dict, Any, Optional, Tuple

try:
    import speech_recognition as sr
except ImportError:
    sr = None

LANGUAGE_CODES = {
    "en": "en-IN",
    "hi": "hi-IN",
    "mr": "mr-IN",
    "hinglish": "hi-IN",
    "en-us": "en-US"
}

class VoiceRecognitionResult:
    def __init__(self, success: bool, transcript: str, language: str, confidence: float = 1.0, error: Optional[str] = None):
        self.success = success
        self.transcript = transcript
        self.language = language
        self.confidence = confidence
        self.error = error
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "transcript": self.transcript,
            "language": self.language,
            "confidence": self.confidence,
            "error": self.error,
            "timestamp": self.timestamp
        }

class VoiceProcessor:
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.is_available = (sr is not None)
        if self.is_available:
            self._init_hardware()

    def _init_hardware(self):
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
            self.microphone = sr.Microphone()
        except Exception as e:
            print(f"[VOICE]: Hardware init error: {e}")
            self.microphone = None

    def listen(self, language_key: str = "en", timeout: int = 5, phrase_time_limit: int = 7) -> VoiceRecognitionResult:
        """
        Listens from the microphone and converts speech to text.
        Supports en-IN, hi-IN, mr-IN.
        """
        if not self.is_available:
            return VoiceRecognitionResult(
                success=False,
                transcript="",
                language=language_key,
                error="SpeechRecognition library or PyAudio is not available."
            )

        if not self.microphone:
            return VoiceRecognitionResult(
                success=False,
                transcript="",
                language=language_key,
                error="No microphone hardware detected."
            )

        lang_code = LANGUAGE_CODES.get(language_key.lower(), "en-IN")

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                print(f"[VOICE]: Listening for spoken command in '{lang_code}' (timeout={timeout}s)...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            print("[VOICE]: Transcribing speech...")
            transcript = self.recognizer.recognize_google(audio, language=lang_code)
            return VoiceRecognitionResult(
                success=True,
                transcript=transcript,
                language=lang_code,
                confidence=0.95
            )
        except sr.WaitTimeoutError:
            return VoiceRecognitionResult(
                success=False,
                transcript="",
                language=lang_code,
                error="Listening timed out with no speech detected."
            )
        except sr.UnknownValueError:
            return VoiceRecognitionResult(
                success=False,
                transcript="",
                language=lang_code,
                error="Speech could not be understood. Please speak clearly or try again."
            )
        except sr.RequestError as e:
            return VoiceRecognitionResult(
                success=False,
                transcript="",
                language=lang_code,
                error=f"Speech recognition service error: {e}"
            )
        except Exception as e:
            return VoiceRecognitionResult(
                success=False,
                transcript="",
                language=lang_code,
                error=f"Microphone error: {e}"
            )
