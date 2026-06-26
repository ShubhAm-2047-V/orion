import sys

try:
    import speech_recognition as sr
except ImportError:
    sr = None

def get_speech_recognizer_and_mic():
    if sr is None:
        return None, None, "The 'speechrecognition' or 'pyaudio' package is not installed."
    
    try:
        recognizer = sr.Recognizer()
        # Calibrate recognizer thresholds
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        
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
    # Import speak inside function to avoid circular imports if any
    from actions import speak
    
    rec, mic, err = get_speech_recognizer_and_mic()
    if err:
        speak(f"Voice error: {err}")
        return None
        
    speak("Listening... Please speak your command.")
    
    try:
        with mic as source:
            # Adjust for ambient noise
            rec.adjust_for_ambient_noise(source, duration=1.0)
            audio = rec.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
        speak("Processing voice command...")
        
        # Recognize speech using Google Speech API
        text = rec.recognize_google(audio)
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
    # Import parse_and_execute inside loop to avoid circular import with main.py
    from main import parse_and_execute
    
    rec, mic, err = get_speech_recognizer_and_mic()
    if err:
        speak(f"Voice loop error: {err}")
        return
        
    speak("Entering continuous voice command loop. Say 'stop listening' or press Ctrl+C to exit.")
    
    while True:
        try:
            with mic as source:
                # Adjust for ambient noise
                rec.adjust_for_ambient_noise(source, duration=0.8)
                print("\n[Voice Mode]: Listening...")
                audio = rec.listen(source, timeout=5, phrase_time_limit=5)
                
            print("[Voice Mode]: Processing...")
            command_text = rec.recognize_google(audio).strip()
            
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
            # Silent timeout in loop mode is fine, just continue
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
            # Prevent crashing, loop continues
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
        
    print("\n\033[36m[JARVIS]: Calibrating microphone for ambient noise...\033[0m")
    try:
        with mic as source:
            rec.adjust_for_ambient_noise(source, duration=1.5)
            # Make response snappier: lower pauses before dispatching
            rec.pause_threshold = 0.5
            # Slow down threshold damping to keep sensitiveness high
            rec.dynamic_energy_adjustment_damping = 0.15
            rec.dynamic_energy_adjustment_ratio = 1.5
    except Exception as e:
        print(f"[JARVIS]: Calibration warning: {e}")
        
    print("\n\033[36m[JARVIS]: Always-listening mode active. Say 'Jarvis ...' to command.\033[0m")
    
    wake_words = ["jarvis", "javis", "travis", "garvis", "jarves", "jarvees", "charvis", "arvis", "jarv"]
    
    while True:
        try:
            with mic as source:
                # None timeout means wait indefinitely for speech to start, stopping CPU spin
                print("\r[Status: Listening for 'Jarvis']...", end="", flush=True)
                audio = rec.listen(source, timeout=None, phrase_time_limit=10)
                
            print("\r[Status: Processing audio]...", end="", flush=True)
            text = rec.recognize_google(audio).strip()
            print(f"\r\033[90m[Heard]: {text}\033[0m", flush=True)
            
            text_lower = text.lower()
            
            # Detect wake words (phonetic variations)
            wake_word_detected = False
            detected_wake = ""
            for ww in wake_words:
                if ww in text_lower:
                    wake_word_detected = True
                    detected_wake = ww
                    break
            
            if wake_word_detected:
                # Extract command after the matched wake word
                match = re.search(rf'\b{detected_wake}\b\s*(.*)', text_lower)
                if match:
                    command = match.group(1).strip()
                    # Preserve casing for proper extraction
                    orig_match = re.search(rf'\b{detected_wake}\b\s*(.*)', text, re.IGNORECASE)
                    orig_command = orig_match.group(1).strip() if orig_match else command
                    
                    if not orig_command:
                        # User only said "Jarvis", ask what they want
                        speak("Yes, sir?")
                        with mic as source:
                            print("\r[Status: Listening for command]...", end="", flush=True)
                            audio_cmd = rec.listen(source, timeout=5, phrase_time_limit=6)
                        print("\r[Status: Processing follow-up]...", end="", flush=True)
                        follow_up = rec.recognize_google(audio_cmd).strip()
                        print(f"\r\033[32m[USER] (Voice):\033[0m {follow_up}", flush=True)
                        parse_and_execute(follow_up)
                    else:
                        print(f"\r\033[32m[USER] (Voice):\033[0m {orig_command}", flush=True)
                        parse_and_execute(orig_command)
                        
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            # Silent fallback for unrecognized background noise
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
