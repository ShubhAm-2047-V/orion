import os
import subprocess
import webbrowser
import platform
import json
import ctypes
import shutil
import threading
import time

_keep_awake_active = False

# Check if pyttsx3 is available for speech feedback
try:
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)     # Speed
    engine.setProperty('volume', 0.9)   # Volume 0-1
    voices = engine.getProperty('voices')
    if len(voices) > 0:
        # Set voice (usually index 0 is Microsoft David - male voice, index 1 is Hazel or Zira - female voice)
        engine.setProperty('voice', voices[0].id)
except ImportError:
    engine = None

def speak(text):
    print(f"\n\033[36m[JARVIS]:\033[0m {text}")
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass

def load_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"applications": {}, "search_engine": "https://www.google.com/search?q=", "safe_commands": []}

def open_app_direct(app_name_lower):
    config = load_config()
    apps = config.get("applications", {})
    
    # 1. Config path
    executable = apps.get(app_name_lower)
    if executable:
        try:
            if executable.startswith("http://") or executable.startswith("https://"):
                webbrowser.open(executable)
            else:
                os.startfile(executable)
            return True
        except Exception:
            if app_name_lower == "whatsapp":
                try:
                    webbrowser.open("https://web.whatsapp.com")
                    return True
                except Exception:
                    pass
            pass
            
    # 2. PATH check
    if shutil.which(app_name_lower) or shutil.which(f"{app_name_lower}.exe"):
        try:
            os.startfile(app_name_lower)
            return True
        except Exception:
            pass
            
    # 3. Protocols
    if app_name_lower in ["whatsapp", "spotify", "discord", "calculator", "skype", "netflix", "instagram", "facebook"]:
        try:
            protocol = f"{app_name_lower}:"
            if app_name_lower == "calculator":
                protocol = "calculator:"
            os.startfile(protocol)
            return True
        except Exception:
            pass
            
    # 4. Start menu shortcuts scan
    start_menu_paths = [
        os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
        os.path.join(os.environ.get("AppData", "C:\\Users\\SHUBHAM\\AppData\\Roaming"), "Microsoft\\Windows\\Start Menu\\Programs")
    ]
    for folder in start_menu_paths:
        if not os.path.exists(folder):
            continue
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(".lnk") and app_name_lower in file.lower():
                    shortcut_path = os.path.join(root, file)
                    try:
                        os.startfile(shortcut_path)
                        # Save in config to load instantly next time
                        config["applications"][app_name_lower] = shortcut_path
                        try:
                            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
                            with open(config_path, 'w') as f:
                                json.dump(config, f, indent=2)
                        except Exception:
                            pass
                        return True
                    except Exception:
                        pass
                        
    # 5. Local AppData search
    local_programs = os.path.join(os.environ.get("LocalAppData", "C:\\Users\\SHUBHAM\\AppData\\Local"), "Programs")
    if os.path.exists(local_programs):
        for root, dirs, files in os.walk(local_programs):
            depth = root.count(os.sep) - local_programs.count(os.sep)
            if depth > 2:
                continue
            for file in files:
                if file.lower() == f"{app_name_lower}.exe":
                    full_path = os.path.join(root, file)
                    try:
                        os.startfile(full_path)
                        config["applications"][app_name_lower] = full_path
                        try:
                            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
                            with open(config_path, 'w') as f:
                                json.dump(config, f, indent=2)
                        except Exception:
                            pass
                        return True
                    except Exception:
                        pass
                        
    return False

def open_app(app_name):
    app_name_lower = app_name.lower().strip()
    if app_name_lower.startswith("open "):
        app_name_lower = app_name_lower[5:].strip()
        
    # 1. Try launching directly first (via config mapping or PATH)
    if open_app_direct(app_name_lower):
        return f"Successfully launched '{app_name_lower}'."
        
    # 2. Fallback: Windows search keystroke simulation
    speak(f"Searching and launching '{app_name_lower}' via Windows search...")
    
    # Escape single quotes for PowerShell SendKeys string safety
    app_name_safe = app_name_lower.replace("'", "''").replace('"', '""')
    
    ps_command = f"""
    $wshell = New-Object -ComObject Wscript.Shell;
    $wshell.SendKeys('^{{ESC}}');
    Start-Sleep -Milliseconds 500;
    $wshell.SendKeys('{app_name_safe}');
    Start-Sleep -Milliseconds 600;
    $wshell.SendKeys('{{ENTER}}');
    """
    
    try:
        subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True, timeout=5)
        return f"Successfully simulated Windows Search search and enter for '{app_name_lower}'."
    except Exception as e:
        return f"Could not launch '{app_name_lower}': {e}"

def run_macro(macro_name):
    config = load_config()
    macros = config.get("macros", {})
    
    macro_name_lower = macro_name.lower().strip()
    apps = macros.get(macro_name_lower)
    
    if not apps:
        return None
        
    speak(f"Activating profile '{macro_name_lower}'. Launching workspace applications...")
    
    successful = []
    failed = []
    
    for app in apps:
        app_clean = app.lower().strip()
        # For bulk launching, direct background launching is cleaner and prevents overlapping visual start menus
        if open_app_direct(app_clean):
            successful.append(app)
        else:
            try:
                os.startfile(app_clean)
                successful.append(app)
            except Exception:
                failed.append(app)
                
    response = []
    if successful:
        response.append(f"Launched: {', '.join(successful)}")
    if failed:
        response.append(f"Failed to locate: {', '.join(failed)}")
        
    return " | ".join(response)

def run_shell_command(command_str):
    speak(f"Executing system command: {command_str}")
    try:
        result = subprocess.run(command_str, shell=True, capture_output=True, text=True, timeout=15)
        output = result.stdout.strip()
        errors = result.stderr.strip()
        
        response = ""
        if output:
            response += f"--- Output ---\n{output}\n"
        if errors:
            response += f"--- Errors ---\n{errors}\n"
        if not response:
            response = "Command executed successfully with no output."
            
        return response
    except subprocess.TimeoutExpired:
        return "Error: Command execution timed out after 15 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"

def search_web(query):
    config = load_config()
    search_url = config.get("search_engine", "https://www.google.com/search?q=")
    full_url = f"{search_url}{query}"
    speak(f"Searching Google for '{query}'...")
    webbrowser.open(full_url)
    return f"Search result page opened in browser: {full_url}"

def open_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    speak(f"Navigating to {url}...")
    webbrowser.open(url)
    return f"Opened website: {url}"

def get_system_status():
    speak("Accessing system diagnostics...")
    info = [
        f"Operating System: {platform.system()} {platform.release()} ({platform.version()})",
        f"Architecture: {platform.machine()}",
        f"Processor: {platform.processor()}"
    ]
    
    # Disk space of main drive
    try:
        total, used, free = shutil.disk_usage("/")
        gb = 1024 * 1024 * 1024
        info.append(f"C: Drive Info: {free/gb:.2f} GB free of {total/gb:.2f} GB total ({used/total*100:.1f}% used)")
    except Exception:
        pass
        
    return "\n".join(info)

def lock_pc():
    speak("Securing workstation. Lock command engaged.")
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Lock command sent to Windows user32."
    except Exception as e:
        return f"Failed to lock workstation: {e}"

def clean_temp():
    speak("Clearing temporary directories, sir.")
    temp_dir = os.environ.get("TEMP")
    if not temp_dir:
        return "System environment TEMP variable not found."
    
    deleted_files = 0
    deleted_folders = 0
    errors = 0
    
    for item in os.listdir(temp_dir):
        path = os.path.join(temp_dir, item)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)
                deleted_files += 1
            elif os.path.isdir(path):
                shutil.rmtree(path)
                deleted_folders += 1
        except Exception:
            errors += 1
            
    return f"Clean complete. Removed {deleted_files} files and {deleted_folders} folders. {errors} active files/folders were in use and skipped."

def close_app(app_name):
    app_name_lower = app_name.lower().strip()
    if app_name_lower.startswith("close "):
        app_name_lower = app_name_lower[6:].strip()
        
    speak(f"Terminating processes matching '{app_name_lower}'...")
    
    # PowerShell script to search for running processes by name, file description, or main window title
    # then terminate them and return their unique process names.
    ps_script = f"""
    $matched = Get-Process | Where-Object {{
        $_.Name -like "*{app_name_lower}*" -or 
        $_.Description -like "*{app_name_lower}*" -or 
        $_.MainWindowTitle -like "*{app_name_lower}*"
    }}
    if ($matched) {{
        $names = $matched | Select-Object -ExpandProperty Name -Unique
        $matched | Stop-Process -Force
        Write-Output ($names -join ', ')
    }} else {{
        Write-Output "NONE"
    }}
    """
    
    try:
        result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, timeout=10)
        output = result.stdout.strip()
        
        if output and output != "NONE":
            return f"Successfully closed processes: {output}."
        else:
            # Fallback to direct taskkill
            res = subprocess.run(f"taskkill /IM {app_name_lower}.exe /F", shell=True, capture_output=True, text=True)
            res_no_ext = subprocess.run(f"taskkill /IM {app_name_lower} /F", shell=True, capture_output=True, text=True)
            if res.returncode == 0 or res_no_ext.returncode == 0:
                return f"Closed process matching '{app_name_lower}' via fallback taskkill."
            return f"Could not find any running processes matching '{app_name_lower}'."
    except Exception as e:
        return f"Error closing processes for '{app_name_lower}': {str(e)}"

def close_current_app():
    speak("Closing active foreground application window...")
    try:
        user32 = ctypes.windll.user32
        jarvis_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if jarvis_hwnd:
            user32.ShowWindow(jarvis_hwnd, 6) # SW_MINIMIZE = 6
            time.sleep(0.4)
        active_hwnd = user32.GetForegroundWindow()
        if active_hwnd and active_hwnd != jarvis_hwnd:
            # Post WM_CLOSE message (0x0010)
            user32.PostMessageW(active_hwnd, 0x0010, 0, 0)
            time.sleep(0.6)
        if jarvis_hwnd:
            user32.ShowWindow(jarvis_hwnd, 9) # SW_RESTORE = 9
        return "Dispatched close message to the active application."
    except Exception as e:
        return f"Failed to execute active window close: {e}"

def minimize_all():
    speak("Minimizing all application windows...")
    ps_code = """
    $shell = New-Object -ComObject Shell.Application
    $shell.MinimizeAll()
    """
    try:
        subprocess.run(["powershell", "-Command", ps_code], capture_output=True, text=True)
        return "All windows minimized."
    except Exception as e:
        return f"Failed to minimize all: {e}"

def maximize_all():
    speak("Restoring all application windows...")
    ps_code = """
    $shell = New-Object -ComObject Shell.Application
    $shell.UndoMinimizeALL()
    """
    try:
        subprocess.run(["powershell", "-Command", ps_code], capture_output=True, text=True)
        return "All windows restored/maximized."
    except Exception as e:
        return f"Failed to restore all: {e}"

def minimize_current_app():
    speak("Minimizing current active window...")
    try:
        user32 = ctypes.windll.user32
        jarvis_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if jarvis_hwnd:
            user32.ShowWindow(jarvis_hwnd, 6) # SW_MINIMIZE = 6
            time.sleep(0.4)
        active_hwnd = user32.GetForegroundWindow()
        if active_hwnd and active_hwnd != jarvis_hwnd:
            user32.ShowWindow(active_hwnd, 6) # SW_MINIMIZE = 6
            time.sleep(0.4)
        if jarvis_hwnd:
            user32.ShowWindow(jarvis_hwnd, 9) # SW_RESTORE = 9
        return "Minimized the active application."
    except Exception as e:
        return f"Failed to minimize active app: {e}"

def maximize_current_app():
    speak("Maximizing current active window...")
    try:
        user32 = ctypes.windll.user32
        jarvis_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if jarvis_hwnd:
            user32.ShowWindow(jarvis_hwnd, 6) # SW_MINIMIZE = 6
            time.sleep(0.4)
        active_hwnd = user32.GetForegroundWindow()
        if active_hwnd and active_hwnd != jarvis_hwnd:
            user32.ShowWindow(active_hwnd, 3) # SW_MAXIMIZE = 3
            time.sleep(0.4)
        if jarvis_hwnd:
            user32.ShowWindow(jarvis_hwnd, 9) # SW_RESTORE = 9
        return "Maximized the active application."
    except Exception as e:
        return f"Failed to maximize active app: {e}"

def find_window_handles(app_name_lower):
    import ctypes
    import ctypes.wintypes
    import os
    
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    
    hwnd_list = []
    
    # Callback type
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    
    def get_window_title(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            return buffer.value
        return ""
        
    def get_process_name(hwnd):
        pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == 0:
            return ""
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        if h_process:
            try:
                buffer = ctypes.create_unicode_buffer(260)
                size = ctypes.wintypes.DWORD(260)
                if kernel32.QueryFullProcessImageNameW(h_process, 0, buffer, ctypes.byref(size)):
                    return os.path.basename(buffer.value).lower()
            except Exception:
                pass
            finally:
                kernel32.CloseHandle(h_process)
        return ""

    def enum_windows_callback(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            title = get_window_title(hwnd).lower()
            proc_name = get_process_name(hwnd)
            
            # Skip empty titles or common shell windows
            if not title or title in ["program manager", "start"]:
                return True
                
            # Match condition
            if app_name_lower in title or app_name_lower in proc_name:
                hwnd_list.append(hwnd)
        return True
        
    cb = WNDENUMPROC(enum_windows_callback)
    user32.EnumWindows(cb, 0)
    return hwnd_list

def maximize_app(app_name):
    app_name_lower = app_name.lower().strip()
    if app_name_lower.startswith("maximize "):
        app_name_lower = app_name_lower[9:].strip()
    elif app_name_lower.startswith("restore "):
        app_name_lower = app_name_lower[8:].strip()
        
    speak(f"Maximizing windows matching '{app_name_lower}'...")
    
    try:
        hwnds = find_window_handles(app_name_lower)
        if hwnds:
            for hwnd in hwnds:
                ctypes.windll.user32.ShowWindow(hwnd, 3) # SW_MAXIMIZE = 3
            return f"Successfully maximized windows matching '{app_name_lower}'."
        else:
            return f"Could not find any running application window matching '{app_name_lower}'."
    except Exception as e:
        return f"Error maximizing '{app_name_lower}': {e}"

def minimize_app(app_name):
    app_name_lower = app_name.lower().strip()
    if app_name_lower.startswith("minimize "):
        app_name_lower = app_name_lower[9:].strip()
        
    speak(f"Minimizing windows matching '{app_name_lower}'...")
    
    try:
        hwnds = find_window_handles(app_name_lower)
        if hwnds:
            for hwnd in hwnds:
                ctypes.windll.user32.ShowWindow(hwnd, 6) # SW_MINIMIZE = 6
            return f"Successfully minimized windows matching '{app_name_lower}'."
        else:
            return f"Could not find any running application window matching '{app_name_lower}'."
    except Exception as e:
        return f"Error minimizing '{app_name_lower}': {e}"

def schedule_open(app_name, delay_val, unit):
    try:
        val = int(delay_val)
    except ValueError:
        return "Error: Delay value must be an integer."
        
    multiplier = 1
    unit_clean = unit.lower().strip()
    if unit_clean.startswith("min"):
        multiplier = 60
    elif unit_clean.startswith("hour"):
        multiplier = 3600
        
    delay_seconds = val * multiplier
    
    def worker():
        time.sleep(delay_seconds)
        open_app(app_name)
        
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    
    speak(f"Timer set to open '{app_name}' in {val} {unit}(s), sir.")
    return f"Successfully scheduled launch of '{app_name}' in {val} {unit}(s)."

def schedule_close(app_name, delay_val, unit):
    try:
        val = int(delay_val)
    except ValueError:
        return "Error: Delay value must be an integer."
        
    multiplier = 1
    unit_clean = unit.lower().strip()
    if unit_clean.startswith("min"):
        multiplier = 60
    elif unit_clean.startswith("hour"):
        multiplier = 3600
        
    delay_seconds = val * multiplier
    
    def worker():
        time.sleep(delay_seconds)
        close_app(app_name)
        
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    
    speak(f"Timer set to close '{app_name}' in {val} {unit}(s), sir.")
    return f"Successfully scheduled termination of '{app_name}' in {val} {unit}(s)."

def snap_app(app_name, direction):
    import ctypes.wintypes
    app_name_lower = app_name.lower().strip()
    direction = direction.lower().strip()
    is_current = (app_name_lower in ["current", "current app", "active", "active app", "current window"])
    
    speak(f"Snapping window to the {direction}...")
    
    try:
        user32 = ctypes.windll.user32
        
        # Get actual work area for a precise snap
        rect = ctypes.wintypes.RECT()
        user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0) # SPI_GETWORKAREA = 0x0030
        work_width = rect.right - rect.left
        work_height = rect.bottom - rect.top
        work_left = rect.left
        work_top = rect.top
        
        jarvis_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        hwnd = 0
        
        if is_current:
            if jarvis_hwnd:
                user32.ShowWindow(jarvis_hwnd, 6) # SW_MINIMIZE = 6
                time.sleep(0.4)
            hwnd = user32.GetForegroundWindow()
        else:
            hwnds = find_window_handles(app_name_lower)
            if hwnds:
                hwnd = hwnds[0]
                
        if hwnd and hwnd != jarvis_hwnd:
            user32.ShowWindow(hwnd, 9) # SW_RESTORE = 9
            
            x, y, cx, cy = 0, 0, 0, 0
            if direction == 'left':
                x = work_left
                y = work_top
                cx = work_width // 2
                cy = work_height
            elif direction == 'right':
                x = work_left + (work_width // 2)
                y = work_top
                cx = work_width // 2
                cy = work_height
            elif direction == 'top':
                x = work_left
                y = work_top
                cx = work_width
                cy = work_height // 2
            elif direction == 'bottom':
                x = work_left
                y = work_top + (work_height // 2)
                cx = work_width
                cy = work_height // 2
                
            user32.SetWindowPos(hwnd, 0, x, y, cx, cy, 0x0040) # SWP_SHOWWINDOW = 0x0040
            
            if jarvis_hwnd:
                time.sleep(0.4)
                user32.ShowWindow(jarvis_hwnd, 9)
                
            return f"Successfully snapped '{app_name_lower}' to the {direction}."
        else:
            if jarvis_hwnd:
                user32.ShowWindow(jarvis_hwnd, 9)
            return f"Could not find any window matching '{app_name_lower}' to snap."
    except Exception as e:
        return f"Error snapping window: {e}"

def switch_to_app(app_name):
    app_name_lower = app_name.lower().strip()
    if app_name_lower.startswith("switch to "):
        app_name_lower = app_name_lower[10:].strip()
    elif app_name_lower.startswith("focus "):
        app_name_lower = app_name_lower[6:].strip()
        
    speak(f"Switching window focus to '{app_name_lower}'...")
    
    try:
        hwnds = find_window_handles(app_name_lower)
        if hwnds:
            hwnd = hwnds[0]
            ctypes.windll.user32.ShowWindow(hwnd, 9) # SW_RESTORE = 9
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            return f"Brought '{app_name_lower}' to the foreground."
        else:
            return f"Could not find any running window matching '{app_name_lower}' to focus."
    except Exception as e:
        return f"Error switching to app: {e}"

def control_volume(target_app, action, level=None):
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    from comtypes import CLSCTX_ALL
    
    target_app_lower = target_app.lower().strip()
    
    # 1. Master Volume Control
    if target_app_lower in ["master", "system", "all", "pc", "speaker", "speakers"]:
        try:
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            if action == "mute":
                volume.SetMute(1, None)
                speak("System volume muted.")
                return "Muted system master volume."
            elif action == "unmute":
                volume.SetMute(0, None)
                speak("System volume unmuted.")
                return "Unmuted system master volume."
            elif action == "set" and level is not None:
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                speak(f"System volume set to {level} percent.")
                return f"Set system master volume to {level}%."
            elif action == "up":
                curr = volume.GetMasterVolumeLevelScalar()
                new_vol = min(1.0, curr + 0.1)
                volume.SetMasterVolumeLevelScalar(new_vol, None)
                pct = int(round(new_vol * 100))
                speak(f"System volume increased to {pct} percent.")
                return f"Increased master volume to {pct}%."
            elif action == "down":
                curr = volume.GetMasterVolumeLevelScalar()
                new_vol = max(0.0, curr - 0.1)
                volume.SetMasterVolumeLevelScalar(new_vol, None)
                pct = int(round(new_vol * 100))
                speak(f"System volume decreased to {pct} percent.")
                return f"Decreased master volume to {pct}%."
        except Exception as e:
            return f"Failed to control master volume: {e}"
            
    # 2. Per-App Volume Control
    try:
        sessions = AudioUtilities.GetAllSessions()
        matched_sessions = []
        for session in sessions:
            volume = session.SimpleAudioVolume
            if session.Process:
                p_name = session.Process.name().lower()
                if target_app_lower in p_name:
                    matched_sessions.append((session.Process.name(), volume))
            elif session.DisplayName and target_app_lower in session.DisplayName.lower():
                matched_sessions.append((session.DisplayName, volume))
                
        if not matched_sessions:
            return f"Could not find any running audio session matching '{target_app}'."
            
        for name, vol in matched_sessions:
            if action == "mute":
                vol.SetMute(1, None)
            elif action == "unmute":
                vol.SetMute(0, None)
            elif action == "set" and level is not None:
                vol.SetMasterVolume(level / 100.0, None)
            elif action == "up":
                curr = vol.GetMasterVolume()
                vol.SetMasterVolume(min(1.0, curr + 0.1), None)
            elif action == "down":
                curr = vol.GetMasterVolume()
                vol.SetMasterVolume(max(0.0, curr - 0.1), None)
                
        names = ", ".join([n for n, _ in matched_sessions])
        if action == "mute":
            speak(f"Muted {target_app}.")
            return f"Muted audio for: {names}."
        elif action == "unmute":
            speak(f"Unmuted {target_app}.")
            return f"Unmuted audio for: {names}."
        elif action == "set":
            speak(f"Set volume for {target_app} to {level} percent.")
            return f"Set volume for {names} to {level}%."
        elif action == "up":
            speak(f"Increased volume for {target_app} by 10 percent.")
            return f"Increased volume for: {names}."
        elif action == "down":
            speak(f"Decreased volume for {target_app} by 10 percent.")
            return f"Decreased volume for: {names}."
    except Exception as e:
        return f"Error controlling volume for '{target_app}': {e}"

def _keep_awake_worker():
    global _keep_awake_active
    user32 = ctypes.windll.user32
    counter = 0
    # VK_F15 = 0x7E
    while _keep_awake_active:
        if counter >= 30:
            user32.keybd_event(0x7E, 0, 0, 0)
            user32.keybd_event(0x7E, 0, 2, 0)
            counter = 0
        time.sleep(1)
        counter += 1

def start_keep_awake():
    global _keep_awake_active
    if _keep_awake_active:
        return "PC is already in keep-awake mode."
    _keep_awake_active = True
    thread = threading.Thread(target=_keep_awake_worker, daemon=True)
    thread.start()
    speak("Keep-awake protocol active. I will prevent the PC from locking or sleeping.")
    return "Successfully activated keep-awake jiggler."

def stop_keep_awake():
    global _keep_awake_active
    if not _keep_awake_active:
        return "Keep-awake protocol is not active."
    _keep_awake_active = False
    speak("Keep-awake protocol deactivated.")
    return "Successfully deactivated keep-awake jiggler."

def set_brightness(level):
    try:
        val = int(level)
    except ValueError:
        return "Error: Brightness level must be an integer between 0 and 100."
    if val < 0 or val > 100:
        return "Error: Brightness level must be between 0 and 100."
        
    speak(f"Setting display brightness to {val} percent...")
    
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(val)
        return f"Successfully set screen brightness to {val}%."
    except Exception as e:
        # Fallback to WMI
        ps_cmd = f"$b = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods; $b.WmiSetBrightness(0, {val})"
        try:
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, timeout=10)
            return f"Successfully set screen brightness to {val}% via WMI fallback."
        except Exception as wmi_err:
            return f"Failed to set screen brightness: {e} (WMI Fallback: {wmi_err})"

def set_power_state(state):
    state_clean = state.lower().strip()
    if state_clean == "sleep":
        speak("Entering sleep state. Goodnight, sir.")
        try:
            # SetSuspendState(Hibernate, ForceCritical, DisableWakeEvent)
            # Hibernate=0, ForceCritical=1, DisableWakeEvent=0
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            return "PC set to sleep mode."
        except Exception as e:
            return f"Failed to set PC to sleep: {e}"
    elif state_clean == "restart":
        speak("Initiating system reboot protocol...")
        try:
            subprocess.run("shutdown.exe /r /t 0", shell=True)
            return "Reboot command sent to OS."
        except Exception as e:
            return f"Failed to reboot: {e}"
    elif state_clean == "shutdown":
        speak("Initiating system shutdown protocol...")
        try:
            subprocess.run("shutdown.exe /s /t 0", shell=True)
            return "Shutdown command sent to OS."
        except Exception as e:
            return f"Failed to shutdown: {e}"
    return "Error: Invalid power state."

def trigger_media_key(key_name):
    key_clean = key_name.lower().strip()
    # Map virtual key codes
    # VK_MEDIA_NEXT_TRACK = 0xB0, VK_MEDIA_PREV_TRACK = 0xB1, VK_MEDIA_PLAY_PAUSE = 0xB3
    vks = {
        "play": 0xB3,
        "pause": 0xB3,
        "next": 0xB0,
        "skip": 0xB0,
        "previous": 0xB1
    }
    
    vk = vks.get(key_clean)
    if not vk:
        return f"Error: Unsupported media key '{key_name}'."
        
    speak(f"Triggering media control command '{key_clean}'...")
    try:
        user32 = ctypes.windll.user32
        user32.keybd_event(vk, 0, 0, 0) # Press
        user32.keybd_event(vk, 0, 2, 0) # Release
        return f"Dispatched multimedia media key code {hex(vk)} to OS."
    except Exception as e:
        return f"Failed to trigger media key: {e}"

def get_battery_status():
    speak("Accessing power diagnostic interface...")
    
    class SYSTEM_POWER_STATUS(ctypes.Structure):
        _fields_ = [
            ('ACLineStatus', ctypes.c_byte),
            ('BatteryFlag', ctypes.c_byte),
            ('BatteryLifePercent', ctypes.c_byte),
            ('SystemStatusFlag', ctypes.c_byte),
            ('BatteryLifeTime', ctypes.c_ulong),
            ('BatteryFullLifeTime', ctypes.c_ulong),
        ]
        
    try:
        status = SYSTEM_POWER_STATUS()
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
            # 1. AC Status
            ac_map = {0: "Battery (Discharging)", 1: "AC Power (Plugged in)", 255: "Unknown"}
            ac_str = ac_map.get(status.ACLineStatus, "Unknown")
            
            # 2. Charge
            pct = status.BatteryLifePercent
            pct_str = f"{pct}%" if pct != 255 else "Unknown"
            
            # 3. Time remaining
            time_rem = status.BatteryLifeTime
            if status.ACLineStatus == 1:
                time_str = "N/A (Connected to Power Source)"
            elif time_rem == 0xffffffff or time_rem == -1:
                time_str = "Calculating..."
            else:
                hours = time_rem // 3600
                mins = (time_rem % 3600) // 60
                time_str = f"{hours}h {mins}m remaining"
                
            report = [
                "--- Battery Diagnostic Log ---",
                f"Power Source: {ac_str}",
                f"Charge Level: {pct_str}",
                f"Discharge Time: {time_str}"
            ]
            return "\n".join(report)
        else:
            return "Failed to query system power status from kernel32."
    except Exception as e:
        return f"Error retrieving battery status: {e}"

def empty_recycle_bin():
    speak("Emptying the Recycle Bin, sir...")
    try:
        res = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        if res == 0:
            speak("Recycle Bin emptied successfully.")
            return "Recycle Bin emptied successfully."
        else:
            if res & 0xFFFFFFFF == 0x80004005:
                speak("Recycle Bin is already empty.")
                return "Recycle Bin is already empty."
            return f"SHEmptyRecycleBinW returned error code: {hex(res)}"
    except Exception as e:
        return f"Failed to empty Recycle Bin: {e}"

def turn_off_screen():
    speak("Powering off display, sir.")
    try:
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
        return "Display sleep signal dispatched."
    except Exception as e:
        return f"Failed to turn off screen: {e}"

def set_system_theme(dark_mode):
    import winreg
    theme_word = "dark" if dark_mode else "light"
    speak(f"Applying Windows {theme_word} mode...")
    val = 0 if dark_mode else 1
    try:
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, val)
        winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, val)
        winreg.CloseKey(key)
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, 0)
        return f"Theme successfully switched to {theme_word} mode."
    except Exception as e:
        return f"Failed to modify theme registry key: {e}"

def control_microphone(action):
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    try:
        mic = AudioUtilities.GetMicrophone()
        interface = mic.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        if action == "mute":
            volume.SetMute(1, None)
            speak("Microphone muted.")
            return "Microphone muted."
        elif action == "unmute":
            volume.SetMute(0, None)
            speak("Microphone unmuted.")
            return "Microphone unmuted."
        elif action == "status":
            muted = volume.GetMute()
            status_str = "muted" if muted else "active"
            speak(f"Microphone is currently {status_str}.")
            return f"Microphone Status: {status_str.upper()}"
    except Exception as e:
        return f"Failed to control microphone: {e}"

def take_screenshot():
    speak("Capturing screen...")
    try:
        from PIL import Image
        timestamp = int(time.time())
        filename = f"screenshot_{timestamp}.png"
        
        screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
            
        filepath = os.path.join(screenshot_dir, filename)
        
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        
        hdesktop = user32.GetDesktopWindow()
        hdc_screen = user32.GetDC(hdesktop)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        
        hbitmap = gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
        gdi32.SelectObject(hdc_mem, hbitmap)
        
        # SRCCOPY = 0x00CC0020
        gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc_screen, 0, 0, 0x00CC0020)
        
        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ('biSize', ctypes.c_uint32),
                ('biWidth', ctypes.c_int32),
                ('biHeight', ctypes.c_int32),
                ('biPlanes', ctypes.c_uint16),
                ('biBitCount', ctypes.c_uint16),
                ('biCompression', ctypes.c_uint32),
                ('biSizeImage', ctypes.c_uint32),
                ('biXPelsPerMeter', ctypes.c_int32),
                ('biYPelsPerMeter', ctypes.c_int32),
                ('biClrUsed', ctypes.c_uint32),
                ('biClrImportant', ctypes.c_uint32),
            ]
            
        class BITMAPINFO(ctypes.Structure):
            _fields_ = [
                ('bmiHeader', BITMAPINFOHEADER),
                ('bmiColors', ctypes.c_uint32 * 3),
            ]
            
        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = width
        bmi.bmiHeader.biHeight = -height
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = 0
        
        buffer = ctypes.create_string_buffer(width * height * 4)
        gdi32.GetDIBits(hdc_screen, hbitmap, 0, height, buffer, ctypes.byref(bmi), 0)
        
        gdi32.DeleteObject(hbitmap)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(hdesktop, hdc_screen)
        
        img = Image.frombytes("RGBA", (width, height), buffer.raw, "raw", "BGRA")
        img.convert("RGB").save(filepath)
        
        speak(f"Screenshot saved as {filename}.")
        return f"Screenshot saved to: {filepath}"
    except Exception as e:
        return f"Failed to take screenshot: {e}"

def clear_clipboard():
    speak("Clearing clipboard history...")
    try:
        user32 = ctypes.windll.user32
        if user32.OpenClipboard(None):
            user32.EmptyClipboard()
            user32.CloseClipboard()
            return "Clipboard successfully cleared."
        return "Error: Could not open clipboard."
    except Exception as e:
        return f"Failed to clear clipboard: {e}"

def manage_virtual_desktop(action):
    speak(f"Triggering virtual desktop command: {action}...")
    try:
        user32 = ctypes.windll.user32
        VK_LWIN = 0x5B
        VK_CONTROL = 0x11
        VK_LEFT = 0x25
        VK_RIGHT = 0x27
        VK_D = 0x44
        VK_F4 = 0x73
        
        if action == "new":
            user32.keybd_event(VK_LWIN, 0, 0, 0)
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_D, 0, 0, 0)
            time.sleep(0.05)
            user32.keybd_event(VK_D, 0, 2, 0)
            user32.keybd_event(VK_CONTROL, 0, 2, 0)
            user32.keybd_event(VK_LWIN, 0, 2, 0)
            return "Created a new virtual desktop."
        elif action == "next":
            user32.keybd_event(VK_LWIN, 0, 0, 0)
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_RIGHT, 0, 0, 0)
            time.sleep(0.05)
            user32.keybd_event(VK_RIGHT, 0, 2, 0)
            user32.keybd_event(VK_CONTROL, 0, 2, 0)
            user32.keybd_event(VK_LWIN, 0, 2, 0)
            return "Switched to the next virtual desktop."
        elif action == "previous":
            user32.keybd_event(VK_LWIN, 0, 0, 0)
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_LEFT, 0, 0, 0)
            time.sleep(0.05)
            user32.keybd_event(VK_LEFT, 0, 2, 0)
            user32.keybd_event(VK_CONTROL, 0, 2, 0)
            user32.keybd_event(VK_LWIN, 0, 2, 0)
            return "Switched to the previous virtual desktop."
        elif action == "close":
            user32.keybd_event(VK_LWIN, 0, 0, 0)
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_F4, 0, 0, 0)
            time.sleep(0.05)
            user32.keybd_event(VK_F4, 0, 2, 0)
            user32.keybd_event(VK_CONTROL, 0, 2, 0)
            user32.keybd_event(VK_LWIN, 0, 2, 0)
            return "Closed the current virtual desktop."
        return "Error: Invalid virtual desktop action."
    except Exception as e:
        return f"Failed to manage virtual desktop: {e}"

def open_settings_page(page_name):
    speak(f"Opening settings for {page_name}...")
    protocols = {
        "wifi": "ms-settings:network-wifi",
        "bluetooth": "ms-settings:bluetooth",
        "update": "ms-settings:windowsupdate",
        "sound": "ms-settings:sound",
        "display": "ms-settings:display"
    }
    protocol = protocols.get(page_name.lower().strip())
    if not protocol:
        protocol = "ms-settings:"
    try:
        os.startfile(protocol)
        return f"Successfully opened settings: {protocol}"
    except Exception as e:
        return f"Failed to open settings page: {e}"

def get_top_processes():
    speak("Analyzing system resource consumption...")
    import psutil
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        top_mem = sorted(processes, key=lambda x: x.get('memory_percent') or 0, reverse=True)[:5]
        
        report = ["--- Top 5 Resource-Consuming Processes ---"]
        for p in top_mem:
            pid = p['pid']
            name = p['name']
            mem = p['memory_percent'] or 0
            cpu = p['cpu_percent'] or 0
            report.append(f"  PID: {pid:<6} | {name:<20} | RAM: {mem:.1f}% | CPU: {cpu:.1f}%")
        return "\n".join(report)
    except Exception as e:
        return f"Failed to retrieve top processes: {e}"

def get_volume_status():
    from pycaw.pycaw import AudioUtilities
    try:
        volume = AudioUtilities.GetSpeakers().EndpointVolume
        muted = volume.GetMute()
        level = int(round(volume.GetMasterVolumeLevelScalar() * 100))
        status_str = "MUTED" if muted else "ACTIVE"
        speak(f"System volume is at {level} percent ({status_str}).")
        return f"System Master Volume: {level}% | Status: {status_str}"
    except Exception as e:
        return f"Failed to retrieve volume status: {e}"

def get_system_idle_time():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    
    try:
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
            seconds = millis / 1000.0
            
            if seconds < 60:
                report = f"System has been idle for {seconds:.1f} seconds."
            else:
                minutes = seconds / 60.0
                report = f"System has been idle for {minutes:.1f} minutes."
                
            speak(report)
            return report
        return "Failed to retrieve idle time using GetLastInputInfo."
    except Exception as e:
        return f"Error retrieving idle time: {e}"

def get_wifi_details():
    speak("Scanning wireless interfaces...")
    try:
        result = subprocess.run("netsh wlan show interfaces", capture_output=True, text=True, shell=True)
        output = result.stdout
        
        ssid = None
        signal = None
        state = None
        
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("SSID") and not line.startswith("BSSID"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    ssid = parts[1].strip()
            elif line.startswith("Signal"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    signal = parts[1].strip()
            elif line.startswith("State"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    state = parts[1].strip()
                    
        if not ssid:
            report = "No active Wi-Fi connection detected."
        else:
            report = f"Wi-Fi Connection Details:\n  SSID: {ssid}\n  Signal Strength: {signal}\n  State: {state}"
            
        speak(report)
        return report
    except Exception as e:
        return f"Failed to retrieve Wi-Fi details: {e}"

def get_disk_breakdown():
    speak("Checking storage partitions, sir...")
    try:
        import psutil
        report = ["--- Disk Storage Space Breakdown ---"]
        gb = 1024 * 1024 * 1024
        
        for part in psutil.disk_partitions():
            if 'cdrom' in part.opts or not part.mountpoint:
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                free_gb = usage.free / gb
                total_gb = usage.total / gb
                used_pct = usage.percent
                report.append(f"  Drive {part.mountpoint:<3} | Free: {free_gb:.2f} GB of {total_gb:.2f} GB total ({used_pct:.1f}% used)")
            except Exception:
                pass
                
        if len(report) == 1:
            return "No active storage partitions detected."
        return "\n".join(report)
    except Exception as e:
        return f"Failed to retrieve disk breakdown: {e}"

def optimize_memory():
    speak("Starting memory optimization protocol...")
    import psutil
    trimmed_count = 0
    
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA = 0x0100
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.info['pid']
            if pid == 0:
                continue
            h_process = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid
            )
            if h_process:
                res = ctypes.windll.psapi.EmptyWorkingSet(h_process)
                if res:
                    trimmed_count += 1
                ctypes.windll.kernel32.CloseHandle(h_process)
        except Exception:
            pass
            
    report = f"Memory optimization complete. Trimmed memory working sets for {trimmed_count} active user processes."
    speak(report)
    return report

def kill_pid(pid_str):
    try:
        pid = int(pid_str)
    except ValueError:
        return "Error: Process ID must be a numeric integer value."
        
    speak(f"Terminating process ID {pid}...")
    try:
        h_process = ctypes.windll.kernel32.OpenProcess(0x0001, False, pid)
        if h_process:
            res = ctypes.windll.kernel32.TerminateProcess(h_process, 0)
            ctypes.windll.kernel32.CloseHandle(h_process)
            if res:
                return f"Successfully terminated process ID {pid}."
        os.kill(pid, 9)
        return f"Successfully terminated process ID {pid}."
    except Exception as e:
        return f"Failed to terminate process ID {pid}: {e}"

def copy_file_path(filename):
    filename = filename.strip('\'"')
    if os.path.isabs(filename):
        abs_path = filename
    else:
        workspace_path = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(workspace_path):
            abs_path = workspace_path
        else:
            abs_path = os.path.abspath(filename)
            
    speak(f"Copying file path to clipboard...")
    try:
        user32 = ctypes.windll.user32
        
        kernel32 = ctypes.windll.kernel32
        kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
        kernel32.GlobalAlloc.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        
        if user32.OpenClipboard(None):
            user32.EmptyClipboard()
            
            unicode_str = str(abs_path)
            h_global = kernel32.GlobalAlloc(0x0042, (len(unicode_str) + 1) * 2)
            if h_global:
                p_global = kernel32.GlobalLock(h_global)
                ctypes.cdll.msvcrt.wcscpy(ctypes.c_wchar_p(p_global), ctypes.c_wchar_p(unicode_str))
                kernel32.GlobalUnlock(h_global)
                user32.SetClipboardData(13, h_global) # CF_UNICODETEXT = 13
            user32.CloseClipboard()
            return f"Copied to clipboard: {abs_path}"
        return "Error: Could not open clipboard to copy path."
    except Exception as e:
        return f"Failed to copy path: {e}"

def get_calendar():
    import calendar
    import datetime
    now = datetime.datetime.now()
    speak(f"Here is the calendar for {now.strftime('%B %Y')}, sir.")
    cal_str = calendar.TextCalendar().formatmonth(now.year, now.month)
    return cal_str

def get_date_time(mode="datetime"):
    import datetime
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p")
    
    if mode == "date":
        report = f"Today is {date_str}."
    elif mode == "time":
        report = f"The current time is {time_str}."
    else:
        report = f"Today is {date_str}, and the current time is {time_str}."
        
    speak(report)
    return report

def add_jarvis_schedule(task_type, trigger_val, command, message=None, interval_mins=None):
    from schedule.scheduler import add_schedule
    import datetime
    try:
        task = add_schedule(task_type, trigger_val, command, message, interval_mins)
        t_id = task["id"]
        if task_type == "alarm":
            speak(f"Alarm ID {t_id} scheduled at {trigger_val}.")
            return f"Scheduled Alarm (ID: {t_id}) at {trigger_val}."
        elif task_type == "one-shot":
            speak(f"Task ID {t_id} scheduled to execute '{command}'.")
            return f"Scheduled Task (ID: {t_id}) to execute '{command}'."
        elif task_type == "recurring":
            speak(f"Recurring task ID {t_id} scheduled to run '{command}' every {interval_mins} minutes.")
            return f"Scheduled Recurring Task (ID: {t_id}) every {interval_mins} min."
    except Exception as e:
        return f"Failed to schedule task: {e}"

def list_jarvis_schedules():
    from schedule.scheduler import load_schedules
    import datetime
    speak("Retrieving active scheduling queue...")
    try:
        schedules = load_schedules()
        if not schedules:
            return "There are no active scheduled tasks or alarms, sir."
            
        report = ["--- Active Scheduling Queue ---"]
        for t in schedules:
            t_id = t.get("id")
            t_type = t.get("type", "unknown").upper()
            cmd = t.get("command")
            
            if t["type"] == "alarm":
                time_val = t.get("alarm_time")
                msg = t.get("message")
                report.append(f"  ID: {t_id:<3} | ALARM | Time: {time_val} | Message: '{msg}'")
            elif t["type"] == "one-shot":
                trig = t.get("trigger_time")
                if isinstance(trig, (int, float)):
                    trig_str = datetime.datetime.fromtimestamp(trig).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    trig_str = trig
                report.append(f"  ID: {t_id:<3} | ONESHOT | Trigger: {trig_str} | Command: '{cmd}'")
            elif t["type"] == "recurring":
                interval = t.get("interval_mins")
                report.append(f"  ID: {t_id:<3} | RECURRING | Every {interval}m | Command: '{cmd}'")
                
        return "\n".join(report)
    except Exception as e:
        return f"Failed to list schedules: {e}"

def cancel_jarvis_schedule(task_id_str):
    from schedule.scheduler import cancel_schedule
    try:
        t_id = int(task_id_str)
    except ValueError:
        return "Error: Schedule ID must be a numeric integer value."
        
    speak(f"Cancelling schedule ID {t_id}...")
    try:
        if cancel_schedule(t_id):
            return f"Successfully cancelled schedule task ID {t_id}."
        return f"Could not find any active schedule matching ID {t_id}."
    except Exception as e:
        return f"Failed to cancel schedule: {e}"

def whatsapp_login():
    speak("Starting WhatsApp Web session authentication...")
    try:
        from whatsapp.automation import whatsapp_login_session
        res = whatsapp_login_session()
        speak("WhatsApp session configuration complete.")
        return res
    except Exception as e:
        return f"Error initiating WhatsApp login: {e}"

def whatsapp_send_msg(target, message):
    speak(f"Preparing to send WhatsApp message to '{target}'...")
    try:
        from whatsapp.automation import send_whatsapp_message
        res = send_whatsapp_message(target, message)
        if "successfully" in res.lower():
            speak(f"WhatsApp message dispatched successfully to {target}.")
        else:
            speak("Failed to deliver WhatsApp message.")
        return res
    except Exception as e:
        return f"Error executing WhatsApp message dispatch: {e}"

def select_file_via_picker():
    # Try Tkinter first
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        
        filepath = filedialog.askopenfilename(
            title="Select File to Send via WhatsApp",
            filetypes=[("All Files", "*.*")]
        )
        root.destroy()
        if filepath:
            return os.path.normpath(filepath)
    except Exception:
        pass
        
    # Try PowerShell OpenFileDialog fallback
    try:
        ps_code = """
        Add-Type -AssemblyName System.Windows.Forms
        $FileBrowser = New-Object System.Windows.Forms.OpenFileDialog
        $FileBrowser.Title = "Select File to Send via WhatsApp"
        $FileBrowser.Filter = "All Files (*.*)|*.*"
        $FileBrowser.ShowHelp = $true
        $Show = $FileBrowser.ShowDialog()
        if ($Show -eq "OK") {
            Write-Output $FileBrowser.FileName
        }
        """
        proc = subprocess.run(
            ["powershell", "-Command", ps_code],
            capture_output=True,
            text=True,
            timeout=20
        )
        if proc.returncode == 0:
            path = proc.stdout.strip()
            if path:
                return os.path.normpath(path)
    except Exception:
        pass
        
    # Terminal fallback
    speak("Please type the absolute path of the file to send:")
    try:
        path = input("[Prompt] Enter file path: ").strip().strip('\'"')
        if os.path.exists(path):
            return os.path.normpath(path)
    except Exception:
        pass
        
    return None

def whatsapp_send_file_action(target, filepath=None):
    if not filepath:
        filepath = select_file_via_picker()
        if not filepath:
            return "Cancelled: No file was selected."
            
    # Normalize filepath: strip any outer quotes that might remain
    filepath = filepath.strip('\'"')
    
    speak(f"Preparing to send file '{os.path.basename(filepath)}' to '{target}' via WhatsApp...")
    try:
        from whatsapp.automation import whatsapp_send_file
        res = whatsapp_send_file(target, filepath)
        if "successfully" in res.lower():
            speak(f"Successfully sent file to {target}.")
        else:
            speak("Failed to send file via WhatsApp.")
        return res
    except Exception as e:
        return f"Error executing WhatsApp file send: {e}"

def whatsapp_unreads_action():
    speak("Scanning for unread WhatsApp messages...")
    try:
        from whatsapp.automation import whatsapp_list_unreads
        res = whatsapp_list_unreads()
        return res
    except Exception as e:
        return f"Error scanning unread WhatsApp messages: {e}"

def whatsapp_auto_reply_action(action, message=None):
    import whatsapp.automation as wa
    action = action.strip().lower()
    if action == "on":
        if not message:
            return "Error: Auto-reply message is required when turning auto-reply ON."
        if wa._auto_reply_active:
            return "WhatsApp auto-reply is already active."
        wa._auto_reply_active = True
        speak(f"Activating WhatsApp auto-reply with message: '{message}'...")
        t = threading.Thread(target=wa.whatsapp_auto_reply_loop, args=(message,), daemon=True)
        t.start()
        return "WhatsApp auto-reply responder initiated in background."
    elif action == "off":
        if not wa._auto_reply_active:
            return "WhatsApp auto-reply is not active."
        wa._auto_reply_active = False
        speak("Deactivating WhatsApp auto-reply responder...")
        return "WhatsApp auto-reply responder deactivated."
    else:
        return f"Error: Unknown auto-reply action '{action}'."

def whatsapp_read_last_action(target):
    speak(f"Checking last message from '{target}'...")
    try:
        from whatsapp.automation import whatsapp_read_last
        res = whatsapp_read_last(target)
        return res
    except Exception as e:
        return f"Error reading last WhatsApp message: {e}"

def whatsapp_status_action(target):
    speak(f"Checking online status of '{target}'...")
    try:
        from whatsapp.automation import whatsapp_get_status
        res = whatsapp_get_status(target)
        return res
    except Exception as e:
        return f"Error checking WhatsApp status: {e}"

def whatsapp_call_action(target, call_type):
    speak(f"Initiating WhatsApp {call_type} call to '{target}'...")
    try:
        from whatsapp.automation import whatsapp_trigger_call
        res = whatsapp_trigger_call(target, call_type)
        return res
    except Exception as e:
        return f"Error initiating WhatsApp call: {e}"

def whatsapp_broadcast_action(targets_str, message):
    speak(f"Initiating WhatsApp broadcast to {targets_str}...")
    try:
        from whatsapp.automation import whatsapp_broadcast
        targets_list = [t.strip() for t in targets_str.split(",") if t.strip()]
        res = whatsapp_broadcast(targets_list, message)
        return res
    except Exception as e:
        return f"Error broadcasting WhatsApp message: {e}"

def whatsapp_mute_action(target, action):
    action_clean = action.strip().lower()
    speak(f"Setting WhatsApp notifications for '{target}' to {action_clean}...")
    try:
        from whatsapp.automation import whatsapp_mute_chat
        res = whatsapp_mute_chat(target, action_clean)
        return res
    except Exception as e:
        return f"Error muting/unmuting WhatsApp chat: {e}"

def whatsapp_logout_action():
    speak("Logging out of WhatsApp and clearing cache...")
    try:
        from whatsapp.automation import whatsapp_logout_session
        res = whatsapp_logout_session()
        speak("WhatsApp session terminated successfully.")
        return res
    except Exception as e:
        return f"Error logging out of WhatsApp: {e}"

