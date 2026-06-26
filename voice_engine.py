import sys
import re
import time
import json
import os

try:
    import speech_recognition as sr
except ImportError:
    sr = None

def load_voice_config():
    """
    Loads voice settings from config.json with safe fallbacks.
    """
    try:
        from actions import load_config
        config = load_config()
    except Exception:
        config = {}
    
    voice_cfg = config.get("voice", {})
    
    # Defaults
    lang = voice_cfg.get("language", "en-IN")
    energy_threshold = voice_cfg.get("energy_threshold", 300)
    dynamic_energy = voice_cfg.get("dynamic_energy_threshold", True)
    pause_threshold = voice_cfg.get("pause_threshold", 0.8)
    phrase_threshold = voice_cfg.get("phrase_threshold", 0.3)
    dynamic_damping = voice_cfg.get("dynamic_energy_adjustment_damping", 0.15)
    dynamic_ratio = voice_cfg.get("dynamic_energy_adjustment_ratio", 1.5)
    
    return {
        "language": lang,
        "energy_threshold": energy_threshold,
        "dynamic_energy_threshold": dynamic_energy,
        "pause_threshold": pause_threshold,
        "phrase_threshold": phrase_threshold,
        "dynamic_energy_adjustment_damping": dynamic_damping,
        "dynamic_energy_adjustment_ratio": dynamic_ratio
    }

def get_speech_recognizer_and_mic():
    if sr is None:
        return None, None, "The 'speechrecognition' or 'pyaudio' package is not installed."
    
    try:
        recognizer = sr.Recognizer()
        cfg = load_voice_config()
        
        # Configure initial thresholds
        recognizer.energy_threshold = cfg["energy_threshold"]
        recognizer.dynamic_energy_threshold = cfg["dynamic_energy_threshold"]
        recognizer.dynamic_energy_adjustment_damping = cfg["dynamic_energy_adjustment_damping"]
        recognizer.dynamic_energy_adjustment_ratio = cfg["dynamic_energy_adjustment_ratio"]
        recognizer.pause_threshold = cfg["pause_threshold"]
        recognizer.phrase_threshold = cfg["phrase_threshold"]
        
        # Test finding microphone
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            return None, None, "No recording microphone hardware detected on this PC."
            
        microphone = sr.Microphone()
        return recognizer, microphone, None
    except Exception as e:
        return None, None, f"Failed to initialize voice hardware: {e}"

def listen_for_command(timeout=5, phrase_time_limit=5):
    """
    Listens for a single voice command from the microphone and returns recognized text.
    Returns None if recognition fails or is not possible.
    """
    from actions import speak
    
    rec, mic, err = get_speech_recognizer_and_mic()
    if err:
        speak(f"Voice error: {err}")
        return None
        
    speak("Listening... Please speak your command.")
    
    try:
        cfg = load_voice_config()
        with mic as source:
            # Adjust for ambient noise
            rec.adjust_for_ambient_noise(source, duration=1.0)
            if rec.energy_threshold > 800:
                rec.energy_threshold = 800
            elif rec.energy_threshold < 100:
                rec.energy_threshold = 100
                
            audio = rec.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
        speak("Processing voice command...")
        
        # Recognize speech using Google Speech API with configured language
        text = rec.recognize_google(audio, language=cfg["language"])
        return text
    except sr.WaitTimeoutError:
        speak("Listening timed out. No speech was detected.")
        return None
    except sr.UnknownValueError:
        speak("I could not understand the audio. Please try again clearly.")
        return None
    except sr.RequestError as e:
        speak(f"Could not request voice results from recognition service: {e}")
        return None
    except Exception as e:
        speak(f"An unexpected error occurred during listening: {e}")
        return None

def voice_loop_mode():
    """
    Enters a continuous loop listening for commands sequentially.
    """
    from actions import speak
    from main import parse_and_execute
    
    rec, mic, err = get_speech_recognizer_and_mic()
    if err:
        speak(f"Voice loop error: {err}")
        return
        
    speak("Entering continuous voice command loop. Say 'stop listening' or press Ctrl+C to exit.")
    
    cfg = load_voice_config()
    
    while True:
        try:
            with mic as source:
                # Adjust for ambient noise
                rec.adjust_for_ambient_noise(source, duration=0.8)
                if rec.energy_threshold > 800:
                    rec.energy_threshold = 800
                elif rec.energy_threshold < 100:
                    rec.energy_threshold = 100
                    
                print("\n[Voice Mode]: Listening...")
                audio = rec.listen(source, timeout=5, phrase_time_limit=5)
                
            print("[Voice Mode]: Processing...")
            command_text = rec.recognize_google(audio, language=cfg["language"]).strip()
            
            # Print voice input clearly
            print(f"\033[32m[USER] (Voice):\033[0m {command_text}")
            
            # Check for exit commands
            command_lower = command_text.lower()
            if command_lower in ["stop listening", "exit voice", "quit voice", "stop voice"]:
                speak("Exiting continuous voice mode.")
                break
                
            # Execute command
            parse_and_execute(command_text)
            
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            print("[Voice Mode]: Audio not recognized.")
            continue
        except sr.RequestError as e:
            speak(f"Voice network error: {e}")
            break
        except KeyboardInterrupt:
            speak("Voice mode interrupted.")
            break
        except Exception as e:
            print(f"[Voice Mode] Error: {e}")
            continue

def always_listening_loop():
    import speech_recognition as sr
    import re
    import time
    from actions import speak
    from main import parse_and_execute
    
    rec, mic, err = get_speech_recognizer_and_mic()
    if err:
        print(f"\n[JARVIS]: Voice hardware error: {err}")
        speak("Voice hardware error, sir. Falling back to text console.")
        # Fall back to console input so the app doesn't crash
        while True:
            try:
                user_input = input(f"\n\033[32m[USER]:\033[0m ")
                parse_and_execute(user_input)
            except (KeyboardInterrupt, SystemExit):
                break
        return
        
    cfg = load_voice_config()
    print("\n\033[36m[JARVIS]: Calibrating microphone for ambient noise...\033[0m")
    try:
        with mic as source:
            rec.adjust_for_ambient_noise(source, duration=1.0)
            
            # Clamp the calibrated energy threshold to prevent desensitization
            if rec.energy_threshold > 800:
                rec.energy_threshold = 800
            elif rec.energy_threshold < 100:
                rec.energy_threshold = 100
                
            rec.pause_threshold = cfg["pause_threshold"]
            rec.phrase_threshold = cfg["phrase_threshold"]
            rec.dynamic_energy_threshold = cfg["dynamic_energy_threshold"]
            rec.dynamic_energy_adjustment_damping = cfg["dynamic_energy_adjustment_damping"]
            rec.dynamic_energy_adjustment_ratio = cfg["dynamic_energy_adjustment_ratio"]
    except Exception as e:
        print(f"[JARVIS]: Calibration warning: {e}")
        
    print(f"\033[36m[JARVIS]: Configured Language: {cfg['language']} | Calibrated Energy Threshold: {rec.energy_threshold:.0f} | Pause Threshold: {rec.pause_threshold}s\033[0m")
    print("\033[36m[JARVIS]: Always-listening mode active. Say 'Jarvis ...' to command.\033[0m")
    
    # Expanded wake words to catch common voice recognition typos/phonetic mistakes
    wake_words = [
        "jarvis", "javis", "travis", "garvis", "jarves", "jarvees", "charvis", "arvis", "jarv",
        "service", "device", "driver", "traverse", "garbage", "jaise", "jobless", "janice",
        "chavez", "jaws", "jarbis", "charlie", "java", "arves", "jervis", "jobless"
    ]
    
    while True:
        try:
            with mic as source:
                print("\r\033[K[Status: Listening for 'Jarvis']...", end="", flush=True)
                audio = rec.listen(source, timeout=None, phrase_time_limit=10)
                
            print("\r\033[K[Status: Processing audio]...", end="", flush=True)
            text = rec.recognize_google(audio, language=cfg["language"]).strip()
            print(f"\r\033[K\033[90m[Heard]: {text}\033[0m", flush=True)
            
            text_lower = text.lower()
            
            # Remove punctuation for wake word matching
            clean_text_lower = re.sub(r'[^\w\s]', '', text_lower).strip()
            
            # Detect wake words (phonetic variations)
            wake_word_detected = False
            detected_wake = ""
            for ww in wake_words:
                if re.search(r'\b' + re.escape(ww) + r'\b', clean_text_lower):
                    wake_word_detected = True
                    detected_wake = ww
                    break
            
            if wake_word_detected:
                # Extract command after the matched wake word from original text
                # We search for the boundary of detected_wake, followed by optional punctuation/spaces
                match = re.search(rf'\b{re.escape(detected_wake)}\b[,\s]*(.*)', text, re.IGNORECASE)
                if match:
                    orig_command = match.group(1).strip()
                    
                    if not orig_command:
                        # User only said "Jarvis", ask what they want
                        speak("Yes, sir?")
                        with mic as source:
                            print("\r\033[K[Status: Listening for command]...", end="", flush=True)
                            audio_cmd = rec.listen(source, timeout=5, phrase_time_limit=6)
                        print("\r\033[K[Status: Processing follow-up]...", end="", flush=True)
                        follow_up = rec.recognize_google(audio_cmd, language=cfg["language"]).strip()
                        print(f"\r\033[32m[USER] (Voice):\033[0m {follow_up}", flush=True)
                        parse_and_execute(follow_up)
                    else:
                        print(f"\r\033[32m[USER] (Voice):\033[0m {orig_command}", flush=True)
                        parse_and_execute(orig_command)
                        
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"\r\033[31m[JARVIS]: Speech API request error: {e}\033[0m", flush=True)
            time.sleep(2)
        except KeyboardInterrupt:
            speak("Powering down. Goodbye, sir.")
            break
        except Exception as e:
            print(f"\r\033[31m[JARVIS]: Loop error: {e}\033[0m", flush=True)
            continue
