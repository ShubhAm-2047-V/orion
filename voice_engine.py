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
