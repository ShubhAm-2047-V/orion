import sys
import re
import threading
import datetime
import time
from actions import (
    speak, open_app, run_shell_command, search_web, open_url, get_system_status, lock_pc, 
    clean_temp, close_app, run_macro, close_current_app, minimize_all, maximize_all, 
    minimize_current_app, maximize_current_app, maximize_app, minimize_app, schedule_open, 
    schedule_close, snap_app, switch_to_app, control_volume, start_keep_awake, stop_keep_awake, 
    set_brightness, set_power_state, trigger_media_key, get_battery_status, empty_recycle_bin, 
    turn_off_screen, set_system_theme, control_microphone, take_screenshot, clear_clipboard, 
    manage_virtual_desktop, open_settings_page, get_top_processes, get_volume_status,
    get_system_idle_time, get_wifi_details, get_disk_breakdown, optimize_memory, kill_pid,
    copy_file_path, get_calendar, get_date_time, add_jarvis_schedule, list_jarvis_schedules,
    cancel_jarvis_schedule, whatsapp_login, whatsapp_send_msg, whatsapp_send_file_action,
    whatsapp_unreads_action, whatsapp_auto_reply_action, whatsapp_read_last_action,
    whatsapp_status_action, whatsapp_call_action, whatsapp_broadcast_action,
    whatsapp_mute_action, whatsapp_logout_action
)
from nlp_engine import translate_to_command

# ANSI Color Codes
COLOR_CYAN = "\033[36m"
COLOR_GREEN = "\033[32m"
COLOR_WHITE = "\033[37m"
COLOR_GRAY = "\033[90m"
COLOR_RESET = "\033[0m"

BANNER = f"""{COLOR_CYAN}============================================================{COLOR_RESET}
{COLOR_WHITE}       ___   _    ___ __   __ ___  ___ 
      |_  | /_\\  | _ \\\\ \\ / /|_ _|/ __|
     / __| / _ \\ |   / \\\\ V /  | | \\__ \\\\
     \\___|/_/ \\_\\|_|_\\  \\_/  |___||___/{COLOR_RESET}
                                       
  {COLOR_GRAY}[ System: Online | Hotkey: Ctrl+Alt+J | Status: OK ]{COLOR_RESET}
{COLOR_CYAN}============================================================{COLOR_RESET}"""

def print_help(category=None):
    category = category.lower().strip() if category else None
    
    if not category:
        print(f"\n{COLOR_CYAN}--- JARVIS CONTROL CORE MENU ---{COLOR_RESET}")
        print(f"To view the available command matrices, type: {COLOR_GREEN}help <category>{COLOR_RESET}")
        print(f"  {COLOR_GREEN}help system{COLOR_RESET}     {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Diagnostics, power states, storage, screens, themes{COLOR_RESET}")
        print(f"  {COLOR_GREEN}help apps{COLOR_RESET}       {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Launch/terminate apps, snap layouts, switching, desktops{COLOR_RESET}")
        print(f"  {COLOR_GREEN}help schedule{COLOR_RESET}   {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Alarms, relative/absolute/recurring command schedules{COLOR_RESET}")
        print(f"  {COLOR_GREEN}help media{COLOR_RESET}      {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}System & per-app volumes, microphone settings, track navigation{COLOR_RESET}")
        print(f"  {COLOR_GREEN}help whatsapp{COLOR_RESET}   {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Selenium Web login, status checking, calls, file picker, logs{COLOR_RESET}")
        print(f"  {COLOR_GREEN}help web{COLOR_RESET}        {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Google web queries, direct site loading shortcuts{COLOR_RESET}")
        print(f"  {COLOR_GREEN}help all{COLOR_RESET}        {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Dump the entire CLI protocol matrix to the console{COLOR_RESET}")
        print(f"{COLOR_CYAN}--------------------------------{COLOR_RESET}")
        return

    show_all = (category == "all")
    header_shown = False

    if show_all or category == "system":
        print(f"\n{COLOR_CYAN}[ SYSTEM & POWER CONTROLS ]{COLOR_RESET}")
        print(f"  {COLOR_GREEN}status{COLOR_RESET}                     {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}View hardware & storage diagnostics.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}battery{COLOR_RESET}                    {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}View power source and battery charge status.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}lock pc{COLOR_RESET}                    {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Lock the workstation screen immediately.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}sleep pc{COLOR_RESET}                   {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Put your computer to sleep mode.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}restart pc{COLOR_RESET}                 {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Initiate a system reboot protocol.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}shutdown pc{COLOR_RESET}                {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Initiate a system shutdown protocol.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}clean temp{COLOR_RESET}                 {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Clear temporary system folders.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}empty trash{COLOR_RESET}                {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Empty the Windows Recycle Bin.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}turn off screen{COLOR_RESET}            {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Put your monitor to sleep immediately.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}dark/light mode{COLOR_RESET}            {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Switch between Windows dark & light themes.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}top processes{COLOR_RESET}              {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}View top 5 RAM consuming active processes.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}idle time{COLOR_RESET}                  {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Check system keyboard/mouse idle duration.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}disk check{COLOR_RESET} / {COLOR_GREEN}storage{COLOR_RESET}       {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Show breakdown of space on all drives.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}optimize memory{COLOR_RESET}            {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Trim RAM working sets of active processes.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}calendar{COLOR_RESET}                   {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Display a calendar of the current month.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}time{COLOR_RESET} / {COLOR_GREEN}date{COLOR_RESET}                {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Check the current time or date details.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}exit{COLOR_RESET} / {COLOR_GREEN}quit{COLOR_RESET}                {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Terminate the Jarvis protocol.{COLOR_RESET}")
        header_shown = True

    if show_all or category == "apps":
        print(f"\n{COLOR_CYAN}[ APPLICATIONS & WINDOWS ]{COLOR_RESET}")
        print(f"  {COLOR_GREEN}open {COLOR_CYAN}<app>{COLOR_RESET}                 {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Launch applications (e.g. {COLOR_GRAY}open chrome{COLOR_WHITE}).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}close {COLOR_CYAN}<app>{COLOR_RESET}                {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Terminate processes (e.g. {COLOR_GRAY}close chrome{COLOR_WHITE}).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}open/close {COLOR_CYAN}<app> in <T>{COLOR_RESET}    {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Scheduled actions (e.g. {COLOR_GRAY}open notepad in 10s{COLOR_WHITE}).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}kill pid {COLOR_CYAN}<id>{COLOR_RESET}              {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Terminate process by process ID.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}copy path {COLOR_CYAN}<file>{COLOR_RESET}           {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Copy absolute file path to clipboard.{COLOR_RESET}")
        print(f"  {COLOR_CYAN}<profile_name>{COLOR_RESET}             {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Run workspace macros (e.g. {COLOR_GRAY}back to work{COLOR_WHITE}).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}snap {COLOR_CYAN}<app> <dir>{COLOR_RESET}           {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Snap window to: {COLOR_CYAN}left, right, top, bottom{COLOR_WHITE}.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}switch to {COLOR_CYAN}<app>{COLOR_RESET}            {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Bring minimized/background app to foreground.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}minimize/maximize {COLOR_CYAN}<app>{COLOR_RESET}    {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Minimize/maximize specific app window.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}minimize/maximize current{COLOR_RESET}  {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Minimize/maximize the active window.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}minimize/maximize all{COLOR_RESET}      {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Minimize all windows or restore them.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}new/close/next desktop{COLOR_RESET}     {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Manage Windows virtual desktops.{COLOR_RESET}")
        header_shown = True

    if show_all or category == "schedule":
        print(f"\n{COLOR_CYAN}[ SCHEDULING & ALARMS ]{COLOR_RESET}")
        print(f"  {COLOR_GREEN}schedule {COLOR_CYAN}<cmd>{COLOR_GREEN} at {COLOR_CYAN}<HH:MM>{COLOR_RESET}      {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Run any Jarvis command at a set time (quotes optional).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}schedule {COLOR_CYAN}<cmd>{COLOR_GREEN} in {COLOR_CYAN}<val><U>{COLOR_RESET}      {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Run command in: {COLOR_CYAN}s, m, h{COLOR_WHITE} (e.g. {COLOR_GRAY}in 5 min{COLOR_WHITE}, quotes optional).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}schedule {COLOR_CYAN}<cmd>{COLOR_GREEN} every {COLOR_CYAN}<val><U>{COLOR_RESET}    {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Run recurring command at set intervals (quotes optional).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}schedule whatsapp to {COLOR_CYAN}<target>{COLOR_GREEN} message {COLOR_CYAN}<msg>{COLOR_GREEN} at {COLOR_CYAN}<HH:MM>{COLOR_RESET}     {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Schedule WhatsApp message at absolute time (quotes optional).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}schedule whatsapp to {COLOR_CYAN}<target>{COLOR_GREEN} message {COLOR_CYAN}<msg>{COLOR_GREEN} in {COLOR_CYAN}<val><U>{COLOR_RESET}     {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Schedule WhatsApp message in relative time (quotes optional).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}schedule whatsapp to {COLOR_CYAN}<target>{COLOR_GREEN} message {COLOR_CYAN}<msg>{COLOR_GREEN} every {COLOR_CYAN}<val><U>{COLOR_RESET}   {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Schedule recurring WhatsApp messages (quotes optional).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}alarm at {COLOR_CYAN}<HH:MM>{COLOR_GREEN} message \"{COLOR_CYAN}<txt>\"{COLOR_RESET} {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Schedule alarm with speech notification.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}schedules{COLOR_RESET} / {COLOR_GREEN}list schedules{COLOR_RESET}   {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}List active alarms and scheduled tasks.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}cancel schedule {COLOR_CYAN}<id>{COLOR_RESET}         {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Cancel scheduled task or alarm by ID.{COLOR_RESET}")
        header_shown = True

    if show_all or category == "media":
        print(f"\n{COLOR_CYAN}[ HARDWARE & MEDIA CONTROLS ]{COLOR_RESET}")
        print(f"  {COLOR_GREEN}brightness {COLOR_CYAN}<0-100>{COLOR_RESET}         {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Set monitor screen brightness level.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}keep awake{COLOR_RESET} / {COLOR_GREEN}stop awake{COLOR_RESET}    {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Toggle mouse jiggler to prevent screen locking.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}volume {COLOR_CYAN}<app> <0-100>{COLOR_RESET}       {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Set volume level (supports app name or {COLOR_CYAN}master{COLOR_WHITE}).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}mute/unmute {COLOR_CYAN}<app>{COLOR_RESET}          {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Mute/unmute volume (supports app name or {COLOR_CYAN}master{COLOR_WHITE}).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}play{COLOR_RESET} / {COLOR_GREEN}pause{COLOR_RESET}               {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Play or pause media playback system-wide.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}next{COLOR_RESET} / {COLOR_GREEN}skip{COLOR_RESET} / {COLOR_GREEN}previous{COLOR_RESET}      {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Skip or go back system-wide media tracks.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}mute/unmute mic{COLOR_RESET}            {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Mute/unmute the recording microphone device.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}volume status{COLOR_RESET}              {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Retrieve master volume percentage & state.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}wifi signal{COLOR_RESET} / {COLOR_GREEN}get ssid{COLOR_RESET}       {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Retrieve connected Wi-Fi connection info.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}screenshot{COLOR_RESET}                 {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Capture desktop screen and save locally.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}clear clipboard{COLOR_RESET}            {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Clear copy-paste clipboard memory.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}voice{COLOR_RESET}                      {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Listen for a single spoken voice command (via Mic).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}voice loop{COLOR_RESET}                 {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Enter continuous hands-free voice command loop mode.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}open {COLOR_CYAN}<item>{COLOR_RESET} settings        {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Deep-link: {COLOR_CYAN}wifi, bluetooth, update, sound, display{COLOR_WHITE}.{COLOR_RESET}")
        header_shown = True

    if show_all or category == "whatsapp":
        print(f"\n{COLOR_CYAN}[ WHATSAPP AUTOMATION ]{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp login{COLOR_RESET}             {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Launch Microsoft Edge to scan and save your login session.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp message to {COLOR_CYAN}<target>{COLOR_RESET} text {COLOR_CYAN}<msg>{COLOR_RESET} {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Send message to contact name or phone number.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp send file to {COLOR_CYAN}<target>{COLOR_RESET} [path {COLOR_CYAN}<path>{COLOR_RESET}] {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Send file to target (pops up a visual file picker if path omitted).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp unreads{COLOR_RESET}           {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}List all contacts with unread messages and their count.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp auto-reply {COLOR_CYAN}<on/off> <msg>{COLOR_RESET} {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Toggle automatic reply responder for incoming messages.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp read last from {COLOR_CYAN}<target>{COLOR_RESET} {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Retrieve and display the last message from a contact.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp status of {COLOR_CYAN}<target>{COLOR_RESET}  {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Check if a contact is online, typing, or offline.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp call/video call {COLOR_CYAN}<target>{COLOR_RESET} {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Initiate a voice or video call.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp broadcast to {COLOR_CYAN}<list>{COLOR_RESET} text {COLOR_CYAN}<msg>{COLOR_RESET} {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Send message to multiple comma-separated contacts.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp mute/unmute {COLOR_CYAN}<target>{COLOR_RESET} {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Toggle notification muting indefinitely for a chat.{COLOR_RESET}")
        print(f"  {COLOR_GREEN}whatsapp logout{COLOR_RESET}            {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Logout from WhatsApp Web and clear local profile cookies.{COLOR_RESET}")
        header_shown = True

    if show_all or category == "web":
        print(f"\n{COLOR_CYAN}[ WEB INTERFACES ]{COLOR_RESET}")
        print(f"  {COLOR_GREEN}website {COLOR_CYAN}<domain>{COLOR_RESET}             {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Open a website (e.g. {COLOR_GRAY}website youtube.com{COLOR_WHITE}).{COLOR_RESET}")
        print(f"  {COLOR_GREEN}search {COLOR_CYAN}<query>{COLOR_RESET}             {COLOR_GRAY}-{COLOR_RESET} {COLOR_WHITE}Perform a Google web search.{COLOR_RESET}")
        header_shown = True

    if header_shown:
        print(f"{COLOR_CYAN}--------------------------------{COLOR_RESET}")

def show_interactive_help():
    import msvcrt
    import os
    import sys
    import threading
    
    if threading.current_thread() is not threading.main_thread():
        print_help()
        return
        
    categories = [
        ("System & Power Controls", "system"),
        ("Applications & Windows", "apps"),
        ("Scheduling & Alarms", "schedule"),
        ("Hardware & Media Controls", "media"),
        ("WhatsApp Automation", "whatsapp"),
        ("Web Interfaces", "web"),
        ("Show All Commands", "all"),
        ("Exit Menu", "exit")
    ]
    
    selected_idx = 0
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    
    try:
        while True:
            os.system('cls')
            print(BANNER)
            print(f"\n{COLOR_CYAN}--- INTERACTIVE HELP MENU ---{COLOR_RESET}")
            print(f"{COLOR_GRAY}Use UP/DOWN arrow keys to navigate, ENTER to select, ESC to exit.{COLOR_RESET}\n")
            
            for i, (name, _) in enumerate(categories):
                if i == selected_idx:
                    print(f" {COLOR_GREEN}➔ {name} {COLOR_RESET}")
                else:
                    print(f"   {COLOR_GRAY}{name}{COLOR_RESET}")
            
            print(f"\n{COLOR_CYAN}============================================================{COLOR_RESET}")
            
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):
                ch2 = msvcrt.getch()
                if ch2 == b'H': # Up Arrow
                    selected_idx = (selected_idx - 1) % len(categories)
                elif ch2 == b'P': # Down Arrow
                    selected_idx = (selected_idx + 1) % len(categories)
            elif ch == b'\r':
                name, key = categories[selected_idx]
                if key == "exit":
                    break
                
                os.system('cls')
                print(BANNER)
                print_help(key)
                print(f"\n{COLOR_GRAY}Press any key to return to help menu...{COLOR_RESET}")
                msvcrt.getch()
            elif ch == b'\x1b': # Esc
                break
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        os.system('cls')
        print(BANNER)

def clean_command_prefixes(cmd):
    cmd_clean = cmd.strip()
    cmd_lower = cmd_clean.lower()
    
    changed = True
    while changed:
        changed = False
        if cmd_lower.startswith("please "):
            cmd_clean = cmd_clean[7:].strip()
            cmd_lower = cmd_clean.lower()
            changed = True
        if cmd_lower.startswith("to "):
            cmd_clean = cmd_clean[3:].strip()
            cmd_lower = cmd_clean.lower()
            changed = True
            
    if cmd_lower.startswith("opening "):
        cmd_clean = "open " + cmd_clean[8:].strip()
    elif cmd_lower.startswith("closing "):
        cmd_clean = "close " + cmd_clean[8:].strip()
        
    return cmd_clean

def parse_and_execute(user_input):
    translated_cmd = translate_to_command(user_input)
    if translated_cmd != user_input:
        print(f"\n{COLOR_CYAN}[JARVIS]: Interpreting query as: '{translated_cmd}'{COLOR_RESET}")
        user_input = translated_cmd

    user_input = clean_command_prefixes(user_input)
    if not user_input:
        return
    
    user_input_lower = user_input.lower()
    
    # 0. Check for macro profiles
    macro_name = user_input_lower
    if macro_name.startswith("profile "):
        macro_name = macro_name[8:].strip()
    elif macro_name.startswith("activate "):
        macro_name = macro_name[9:].strip()
    elif macro_name.startswith("macro "):
        macro_name = macro_name[6:].strip()
        
    macro_res = run_macro(macro_name)
    if macro_res:
        print(f"\n[JARVIS]: Profile activation complete. {macro_res}")
        return
        
    # 1. Exit commands
    if user_input_lower in ['exit', 'quit', 'shutdown jarvis', 'bye', 'shutdown']:
        speak("Terminating system session. Goodbye, sir.")
        sys.exit(0)
        
    # 2. Help commands
    help_match = re.match(r'^(?:help|commands|menu|matrix)(?:\s+(system|apps|schedule|media|whatsapp|web|all))?$', user_input_lower)
    if help_match:
        category = help_match.group(1)
        if category:
            print_help(category)
        else:
            show_interactive_help()
        return
    if user_input_lower in ['what can you do']:
        show_interactive_help()
        return

    # 2.5 Voice command triggers
    if re.match(r'^(?:voice|listen|speak|speak\s+command)$', user_input_lower):
        from voice_engine import listen_for_command
        voice_cmd = listen_for_command()
        if voice_cmd:
            print(f"\033[32m[USER] (Voice):\033[0m {voice_cmd}")
            parse_and_execute(voice_cmd)
        return
        
    if re.match(r'^(?:voice\s+loop|listen\s+loop|voice\s+mode|continuous\s+listening)$', user_input_lower):
        from voice_engine import voice_loop_mode
        voice_loop_mode()
        return

    # 3. System Status
    if re.match(r'^(system\s+status|status|diagnostics|sysinfo|system)$', user_input_lower):
        status = get_system_status()
        print(f"\n{status}")
        return

    # 4. Lock PC
    if re.match(r'^(lock\s+pc|lock\s+screen|lock\s+workstation)$', user_input_lower):
        res = lock_pc()
        print(f"\n{res}")
        return

    # 5. Clean Temp
    if re.match(r'^(clean\s+temp|clear\s+temp|clean\s+temporary)$', user_input_lower):
        res = clean_temp()
        print(f"\n{res}")
        return

    # Empty Recycle Bin
    if re.match(r'^(empty\s+trash|empty\s+recycle\s+bin)$', user_input_lower):
        res = empty_recycle_bin()
        print(f"\n{res}")
        return

    # Turn Off Screen
    if re.match(r'^(turn\s+off\s+screen|turn\s+off\s+display|display\s+sleep)$', user_input_lower):
        res = turn_off_screen()
        print(f"\n{res}")
        return

    # Toggle Dark/Light Theme
    if re.match(r'^(dark\s+mode|light\s+mode)$', user_input_lower):
        res = set_system_theme(user_input_lower == "dark mode")
        print(f"\n{res}")
        return

    # Microphone Controls
    mic_match = re.match(r'^(mute\s+mic|unmute\s+mic|microphone\s+status|mic\s+status)$', user_input_lower)
    if mic_match:
        cmd = mic_match.group(1)
        if "unmute" in cmd:
            action = "unmute"
        elif "mute" in cmd:
            action = "mute"
        else:
            action = "status"
        res = control_microphone(action)
        print(f"\n{res}")
        return

    # Take Screenshot
    if re.match(r'^(screenshot|take\s+screenshot|capture\s+screen)$', user_input_lower):
        res = take_screenshot()
        print(f"\n{res}")
        return

    # Clear Clipboard
    if re.match(r'^(clear\s+clipboard|empty\s+clipboard)$', user_input_lower):
        res = clear_clipboard()
        print(f"\n{res}")
        return

    # Virtual Desktop Controls
    vdesktop_match = re.match(r'^(new\s+desktop|close\s+desktop|next\s+desktop|prev\s+desktop|previous\s+desktop)$', user_input_lower)
    if vdesktop_match:
        cmd = vdesktop_match.group(1)
        if "new" in cmd:
            action = "new"
        elif "close" in cmd:
            action = "close"
        elif "next" in cmd:
            action = "next"
        else:
            action = "previous"
        res = manage_virtual_desktop(action)
        print(f"\n{res}")
        return

    # Settings Deep-Links
    settings_match = re.match(r'^open\s+(wifi|bluetooth|update|sound|display)\s+settings$', user_input_lower)
    if settings_match:
        page = settings_match.group(1)
        res = open_settings_page(page)
        print(f"\n{res}")
        return

    # WhatsApp Automation Login Session
    if re.match(r'^(whatsapp\s+login|whatsapp\s+auth|whatsapp\s+authenticate)$', user_input_lower):
        res = whatsapp_login()
        print(f"\n{res}")
        return

    # WhatsApp Send Message: whatsapp message to "John Doe" text "Hello" (quotes optional)
    wa_msg_match = re.match(r'^whatsapp\s+message\s+to\s+("?)(.+?)\1\s+text\s+("?)(.+?)\3$', user_input_lower)
    if wa_msg_match:
        wa_msg_orig = re.match(r'^whatsapp\s+message\s+to\s+("?)(.+?)\1\s+text\s+("?)(.+?)\3$', user_input, re.IGNORECASE)
        if wa_msg_orig:
            target_val = wa_msg_orig.group(2).strip()
            message_val = wa_msg_orig.group(4).strip()
            res = whatsapp_send_msg(target_val, message_val)
            print(f"\n{res}")
            return

    # WhatsApp Send File: whatsapp send file to "John Doe" path "C:\file.png" (quotes optional)
    wa_file_match = re.match(r'^whatsapp\s+send\s+file\s+to\s+("?)(.+?)\1\s+path\s+("?)(.+?)\3$', user_input_lower)
    if wa_file_match:
        wa_file_orig = re.match(r'^whatsapp\s+send\s+file\s+to\s+("?)(.+?)\1\s+path\s+("?)(.+?)\3$', user_input, re.IGNORECASE)
        if wa_file_orig:
            target_val = wa_file_orig.group(2).strip()
            filepath_val = wa_file_orig.group(4).strip()
            res = whatsapp_send_file_action(target_val, filepath_val)
            print(f"\n{res}")
            return

    # WhatsApp Send File via Picker: whatsapp send file to "John Doe" (quotes optional)
    wa_file_picker_match = re.match(r'^whatsapp\s+send\s+file\s+to\s+("?)(.+?)\1$', user_input_lower)
    if wa_file_picker_match:
        wa_file_picker_orig = re.match(r'^whatsapp\s+send\s+file\s+to\s+("?)(.+?)\1$', user_input, re.IGNORECASE)
        if wa_file_picker_orig:
            target_val = wa_file_picker_orig.group(2).strip()
            res = whatsapp_send_file_action(target_val, None)
            print(f"\n{res}")
            return

    # WhatsApp List Unreads: whatsapp unreads
    if re.match(r'^(whatsapp\s+unreads|whatsapp\s+unread\s+messages|whatsapp\s+unread)$', user_input_lower):
        res = whatsapp_unreads_action()
        print(f"\n{res}")
        return

    # WhatsApp Auto-Reply: whatsapp auto-reply on "message" / whatsapp auto-reply off
    wa_reply_match = re.match(r'^whatsapp\s+auto[- ]reply\s+(on|off)(?:\s+("?)(.+?)\2)?$', user_input_lower)
    if wa_reply_match:
        wa_reply_orig = re.match(r'^whatsapp\s+auto[- ]reply\s+(on|off)(?:\s+("?)(.+?)\2)?$', user_input, re.IGNORECASE)
        if wa_reply_orig:
            action_val = wa_reply_orig.group(1).strip().lower()
            msg_val = wa_reply_orig.group(3).strip() if wa_reply_orig.group(3) else None
            res = whatsapp_auto_reply_action(action_val, msg_val)
            print(f"\n{res}")
            return

    # WhatsApp Read Last: whatsapp read last from "John Doe"
    wa_read_match = re.match(r'^whatsapp\s+read\s+last\s+(?:from|of)\s+("?)(.+?)\1$', user_input_lower)
    if wa_read_match:
        wa_read_orig = re.match(r'^whatsapp\s+read\s+last\s+(?:from|of)\s+("?)(.+?)\1$', user_input, re.IGNORECASE)
        if wa_read_orig:
            target_val = wa_read_orig.group(2).strip()
            res = whatsapp_read_last_action(target_val)
            print(f"\n{res}")
            return

    # WhatsApp Online Status: whatsapp status of "John Doe"
    wa_status_match = re.match(r'^whatsapp\s+(?:online\s+)?status\s+(?:of\s+)?("?)(.+?)\1$', user_input_lower)
    if wa_status_match:
        wa_status_orig = re.match(r'^whatsapp\s+(?:online\s+)?status\s+(?:of\s+)?("?)(.+?)\1$', user_input, re.IGNORECASE)
        if wa_status_orig:
            target_val = wa_status_orig.group(2).strip()
            res = whatsapp_status_action(target_val)
            print(f"\n{res}")
            return

    # WhatsApp Call: whatsapp call "John Doe" / whatsapp video call "John Doe"
    wa_call_match = re.match(r'^whatsapp\s+(video\s+)?call\s+("?)(.+?)\2$', user_input_lower)
    if wa_call_match:
        wa_call_orig = re.match(r'^whatsapp\s+(video\s+)?call\s+("?)(.+?)\2$', user_input, re.IGNORECASE)
        if wa_call_orig:
            is_video = wa_call_orig.group(1) is not None
            call_type = "video" if is_video else "voice"
            target_val = wa_call_orig.group(3).strip()
            res = whatsapp_call_action(target_val, call_type)
            print(f"\n{res}")
            return

    # WhatsApp Broadcast: whatsapp broadcast to "John, Mary" text "Hello"
    wa_broadcast_match = re.match(r'^whatsapp\s+broadcast\s+to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3$', user_input_lower)
    if wa_broadcast_match:
        wa_broadcast_orig = re.match(r'^whatsapp\s+broadcast\s+to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3$', user_input, re.IGNORECASE)
        if wa_broadcast_orig:
            targets_val = wa_broadcast_orig.group(2).strip()
            message_val = wa_broadcast_orig.group(4).strip()
            res = whatsapp_broadcast_action(targets_val, message_val)
            print(f"\n{res}")
            return

    # WhatsApp Mute/Unmute: whatsapp mute "John Doe" / whatsapp unmute "John Doe"
    wa_mute_match = re.match(r'^whatsapp\s+(mute|unmute)\s+("?)(.+?)\2$', user_input_lower)
    if wa_mute_match:
        wa_mute_orig = re.match(r'^whatsapp\s+(mute|unmute)\s+("?)(.+?)\2$', user_input, re.IGNORECASE)
        if wa_mute_orig:
            action_val = wa_mute_orig.group(1).strip().lower()
            target_val = wa_mute_orig.group(3).strip()
            res = whatsapp_mute_action(target_val, action_val)
            print(f"\n{res}")
            return

    # WhatsApp Logout: whatsapp logout
    if re.match(r'^(whatsapp\s+logout|whatsapp\s+signout|whatsapp\s+sign\s+out)$', user_input_lower):
        res = whatsapp_logout_action()
        print(f"\n{res}")
        return

    # Top Process Monitor
    if re.match(r'^(top\s+processes|top\s+apps|resource\s+usage)$', user_input_lower):
        res = get_top_processes()
        print(f"\n{res}")
        return

    # Volume Status
    if re.match(r'^(volume\s+status|get\s+volume)$', user_input_lower):
        res = get_volume_status()
        print(f"\n{res}")
        return

    # Alarm Trigger: alarm at 08:30 message "Time for work"
    alarm_match = re.match(r'^alarm\s+at\s+(\d{1,2}:\d{2})\s+message\s+"([^"]+)"$', user_input_lower)
    if alarm_match:
        alarm_match_orig = re.match(r'^alarm\s+at\s+(\d{1,2}:\d{2})\s+message\s+"([^"]+)"$', user_input, re.IGNORECASE)
        if alarm_match_orig:
            time_val = alarm_match_orig.group(1).strip()
            msg_val = alarm_match_orig.group(2).strip()
            if len(time_val.split(":")[0]) == 1:
                time_val = "0" + time_val
            res = add_jarvis_schedule("alarm", time_val, "alarm", msg_val)
            print(f"\n{res}")
            return

    # Helper to parse YYYY-MM-DD or DD-MM-YYYY with HH:MM into standard string format
    def format_sched_date_time(date_str, time_str):
        if len(time_str.split(":")[0]) == 1:
            time_str = "0" + time_str
        if "-" in date_str:
            parts = date_str.split("-")
            if len(parts[0]) == 4: # YYYY-MM-DD
                return f"{date_str} {time_str}:00"
            else: # DD-MM-YYYY
                return f"{parts[2]}-{parts[1]}-{parts[0]} {time_str}:00"
        return f"{date_str} {time_str}:00"

    # WhatsApp Specific Schedule with Date (using "on <date> at <time>", quotes optional)
    wa_sched_date_on = re.match(r'^schedule\s+whatsapp\s+(?:message\s+)?to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3\s+on\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+at\s+(\d{1,2}:\d{2})$', user_input_lower)
    if wa_sched_date_on:
        wa_sched_date_on_orig = re.match(r'^schedule\s+whatsapp\s+(?:message\s+)?to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3\s+on\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+at\s+(\d{1,2}:\d{2})$', user_input, re.IGNORECASE)
        if wa_sched_date_on_orig:
            target_val = wa_sched_date_on_orig.group(2).strip()
            message_val = wa_sched_date_on_orig.group(4).strip()
            date_val = wa_sched_date_on_orig.group(5).strip()
            time_val = wa_sched_date_on_orig.group(6).strip()
            target_dt_str = format_sched_date_time(date_val, time_val)
            
            standard_cmd = f'whatsapp message to "{target_val}" text "{message_val}"'
            res = add_jarvis_schedule("one-shot", target_dt_str, standard_cmd)
            print(f"\n{res}")
            return

    # WhatsApp Specific Schedule with Date (using "at <date> <time>", quotes optional)
    wa_sched_date_at = re.match(r'^schedule\s+whatsapp\s+(?:message\s+)?to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3\s+at\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+(\d{1,2}:\d{2})$', user_input_lower)
    if wa_sched_date_at:
        wa_sched_date_at_orig = re.match(r'^schedule\s+whatsapp\s+(?:message\s+)?to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3\s+at\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+(\d{1,2}:\d{2})$', user_input, re.IGNORECASE)
        if wa_sched_date_at_orig:
            target_val = wa_sched_date_at_orig.group(2).strip()
            message_val = wa_sched_date_at_orig.group(4).strip()
            date_val = wa_sched_date_at_orig.group(5).strip()
            time_val = wa_sched_date_at_orig.group(6).strip()
            target_dt_str = format_sched_date_time(date_val, time_val)
            
            standard_cmd = f'whatsapp message to "{target_val}" text "{message_val}"'
            res = add_jarvis_schedule("one-shot", target_dt_str, standard_cmd)
            print(f"\n{res}")
            return

    # General Schedule with Date (using "on <date> at <time>", quotes optional)
    sched_date_on = re.match(r'^schedule\s+("?)(.+?)\1\s+on\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+at\s+(\d{1,2}:\d{2})$', user_input_lower)
    if sched_date_on:
        sched_date_on_orig = re.match(r'^schedule\s+("?)(.+?)\1\s+on\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+at\s+(\d{1,2}:\d{2})$', user_input, re.IGNORECASE)
        if sched_date_on_orig:
            cmd_val = clean_command_prefixes(sched_date_on_orig.group(2).strip())
            date_val = sched_date_on_orig.group(3).strip()
            time_val = sched_date_on_orig.group(4).strip()
            target_dt_str = format_sched_date_time(date_val, time_val)
            res = add_jarvis_schedule("one-shot", target_dt_str, cmd_val)
            print(f"\n{res}")
            return

    # General Schedule with Date (using "at <date> <time>", quotes optional)
    sched_date_at = re.match(r'^schedule\s+("?)(.+?)\1\s+at\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+(\d{1,2}:\d{2})$', user_input_lower)
    if sched_date_at:
        sched_date_at_orig = re.match(r'^schedule\s+("?)(.+?)\1\s+at\s+(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+(\d{1,2}:\d{2})$', user_input, re.IGNORECASE)
        if sched_date_at_orig:
            cmd_val = clean_command_prefixes(sched_date_at_orig.group(2).strip())
            date_val = sched_date_at_orig.group(3).strip()
            time_val = sched_date_at_orig.group(4).strip()
            target_dt_str = format_sched_date_time(date_val, time_val)
            res = add_jarvis_schedule("one-shot", target_dt_str, cmd_val)
            print(f"\n{res}")
            return

    # WhatsApp Specific Schedule Absolute: schedule whatsapp [message] to <target> text/message <msg> at <time> (quotes optional)
    wa_sched_abs = re.match(r'^schedule\s+whatsapp\s+(?:message\s+)?to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3\s+at\s+(\d{1,2}:\d{2})$', user_input_lower)
    if wa_sched_abs:
        wa_sched_abs_orig = re.match(r'^schedule\s+whatsapp\s+(?:message\s+)?to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3\s+at\s+(\d{1,2}:\d{2})$', user_input, re.IGNORECASE)
        if wa_sched_abs_orig:
            target_val = wa_sched_abs_orig.group(2).strip()
            message_val = wa_sched_abs_orig.group(4).strip()
            time_val = wa_sched_abs_orig.group(5).strip()
            if len(time_val.split(":")[0]) == 1:
                time_val = "0" + time_val
            now_dt = datetime.datetime.now()
            target_dt_str = f"{now_dt.strftime('%Y-%m-%d')} {time_val}:00"
            target_dt = datetime.datetime.strptime(target_dt_str, "%Y-%m-%d %H:%M:%S")
            if now_dt > target_dt:
                target_dt += datetime.timedelta(days=1)
                target_dt_str = target_dt.strftime("%Y-%m-%d %H:%M:%S")
            
            standard_cmd = f'whatsapp message to "{target_val}" text "{message_val}"'
            res = add_jarvis_schedule("one-shot", target_dt_str, standard_cmd)
            print(f"\n{res}")
            return

    # WhatsApp Specific Schedule Relative: schedule whatsapp [message] to <target> text/message <msg> in <val><unit> (quotes optional)
    wa_sched_rel = re.match(r'^schedule\s+whatsapp\s+(?:message\s+)?to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3\s+in\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input_lower)
    if wa_sched_rel:
        wa_sched_rel_orig = re.match(r'^schedule\s+whatsapp\s+(?:message\s+)?to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3\s+in\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input, re.IGNORECASE)
        if wa_sched_rel_orig:
            target_val = wa_sched_rel_orig.group(2).strip()
            message_val = wa_sched_rel_orig.group(4).strip()
            val_val = int(wa_sched_rel_orig.group(5).strip())
            unit_val = wa_sched_rel_orig.group(6).strip().lower()
            
            multiplier = 1
            if unit_val.startswith("m"):
                multiplier = 60
            elif unit_val.startswith("h"):
                multiplier = 3600
                
            trigger_time = time.time() + (val_val * multiplier)
            standard_cmd = f'whatsapp message to "{target_val}" text "{message_val}"'
            res = add_jarvis_schedule("one-shot", trigger_time, standard_cmd)
            print(f"\n{res}")
            return

    # WhatsApp Specific Schedule Recurring: schedule whatsapp [message] to <target> text/message <msg> every <val><unit> (quotes optional)
    wa_sched_rec = re.match(r'^schedule\s+whatsapp\s+(?:message\s+)?to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3\s+every\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input_lower)
    if wa_sched_rec:
        wa_sched_rec_orig = re.match(r'^schedule\s+whatsapp\s+(?:message\s+)?to\s+("?)(.+?)\1\s+(?:text|message)\s+("?)(.+?)\3\s+every\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input, re.IGNORECASE)
        if wa_sched_rec_orig:
            target_val = wa_sched_rec_orig.group(2).strip()
            message_val = wa_sched_rec_orig.group(4).strip()
            val_val = int(wa_sched_rec_orig.group(5).strip())
            unit_val = wa_sched_rec_orig.group(6).strip().lower()
            
            if unit_val.startswith("s"):
                mins_val = val_val / 60.0
            elif unit_val.startswith("h"):
                mins_val = val_val * 60
            else:
                mins_val = val_val
                
            standard_cmd = f'whatsapp message to "{target_val}" text "{message_val}"'
            res = add_jarvis_schedule("recurring", None, standard_cmd, interval_mins=mins_val)
            print(f"\n{res}")
            return

    # Schedule Absolute Time: schedule "lock pc" at 18:30 (quotes optional)
    sched_abs_match = re.match(r'^schedule\s+("?)(.+?)\1\s+at\s+(\d{1,2}:\d{2})$', user_input_lower)
    if sched_abs_match:
        sched_abs_orig = re.match(r'^schedule\s+("?)(.+?)\1\s+at\s+(\d{1,2}:\d{2})$', user_input, re.IGNORECASE)
        if sched_abs_orig:
            cmd_val = clean_command_prefixes(sched_abs_orig.group(2).strip())
            time_val = sched_abs_orig.group(3).strip()
            if len(time_val.split(":")[0]) == 1:
                time_val = "0" + time_val
            now_dt = datetime.datetime.now()
            target_dt_str = f"{now_dt.strftime('%Y-%m-%d')} {time_val}:00"
            target_dt = datetime.datetime.strptime(target_dt_str, "%Y-%m-%d %H:%M:%S")
            if now_dt > target_dt:
                target_dt += datetime.timedelta(days=1)
                target_dt_str = target_dt.strftime("%Y-%m-%d %H:%M:%S")
            res = add_jarvis_schedule("one-shot", target_dt_str, cmd_val)
            print(f"\n{res}")
            return

    # Schedule Relative Interval: schedule "volume 30" in 20 min (quotes optional)
    sched_rel_match = re.match(r'^schedule\s+("?)(.+?)\1\s+in\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input_lower)
    if sched_rel_match:
        sched_rel_orig = re.match(r'^schedule\s+("?)(.+?)\1\s+in\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input, re.IGNORECASE)
        if sched_rel_orig:
            cmd_val = clean_command_prefixes(sched_rel_orig.group(2).strip())
            val_val = int(sched_rel_orig.group(3).strip())
            unit_val = sched_rel_orig.group(4).strip().lower()
            
            multiplier = 1
            if unit_val.startswith("m"):
                multiplier = 60
            elif unit_val.startswith("h"):
                multiplier = 3600
                
            trigger_time = time.time() + (val_val * multiplier)
            res = add_jarvis_schedule("one-shot", trigger_time, cmd_val)
            print(f"\n{res}")
            return

    # Schedule Recurring: schedule "clean temp" every 60 min (quotes optional)
    sched_rec_match = re.match(r'^schedule\s+("?)(.+?)\1\s+every\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input_lower)
    if sched_rec_match:
        sched_rec_orig = re.match(r'^schedule\s+("?)(.+?)\1\s+every\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input, re.IGNORECASE)
        if sched_rec_orig:
            cmd_val = clean_command_prefixes(sched_rec_orig.group(2).strip())
            val_val = int(sched_rec_orig.group(3).strip())
            unit_val = sched_rec_orig.group(4).strip().lower()
            
            if unit_val.startswith("s"):
                mins_val = val_val / 60.0
            elif unit_val.startswith("h"):
                mins_val = val_val * 60
            else:
                mins_val = val_val
                
            res = add_jarvis_schedule("recurring", None, cmd_val, interval_mins=mins_val)
            print(f"\n{res}")
            return

    # List schedules
    if re.match(r'^(show\s+schedules|list\s+schedules|schedules)$', user_input_lower):
        res = list_jarvis_schedules()
        print(f"\n{res}")
        return

    # Cancel schedule
    cancel_sched_match = re.match(r'^cancel\s+schedule\s+(\d+)$', user_input_lower)
    if cancel_sched_match:
        id_val = cancel_sched_match.group(1)
        res = cancel_jarvis_schedule(id_val)
        print(f"\n{res}")
        return

    # System Idle Time Detector
    if re.match(r'^(idle\s+time|get\s+idle)$', user_input_lower):
        res = get_system_idle_time()
        print(f"\n{res}")
        return

    # Wi-Fi Signal & SSID Reporting
    if re.match(r'^(wifi\s+signal|get\s+ssid)$', user_input_lower):
        res = get_wifi_details()
        print(f"\n{res}")
        return

    # Disk Space Breakdown (All Drives)
    if re.match(r'^(disk\s+check|storage\s+status|storage\s+check)$', user_input_lower):
        res = get_disk_breakdown()
        print(f"\n{res}")
        return

    # Optimize Memory (RAM Trim)
    if re.match(r'^(optimize\s+memory|trim\s+ram|clean\s+ram)$', user_input_lower):
        res = optimize_memory()
        print(f"\n{res}")
        return

    # Process Killer by ID (PID)
    kill_pid_match = re.match(r'^kill\s+pid\s+(\d+)$', user_input_lower)
    if kill_pid_match:
        pid_val = kill_pid_match.group(1)
        res = kill_pid(pid_val)
        print(f"\n{res}")
        return

    # Copy Absolute File Path to Clipboard
    copy_path_match = re.match(r'^copy\s+path\s+(.+)$', user_input_lower)
    if copy_path_match:
        filename_val = copy_path_match.group(1)
        res = copy_file_path(filename_val)
        print(f"\n{res}")
        return

    # Interactive Calendar
    if re.match(r'^(calendar|month)$', user_input_lower):
        res = get_calendar()
        print(f"\n{res}")
        return

    # Date-Time Controls
    datetime_match = re.match(r'^(time|date)$', user_input_lower)
    if datetime_match:
        mode = datetime_match.group(1)
        res = get_date_time(mode)
        print(f"\n{res}")
        return

    # 6.3 Timed/Scheduled Controls (Persistent Scheduler integration)
    # Open app relative: open chrome in 10 minutes
    sched_open_match = re.match(r'^open\s+([a-zA-Z0-9_\-\.\s]+)\s+in\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input_lower)
    if sched_open_match:
        sched_open_orig = re.match(r'^open\s+([a-zA-Z0-9_\-\.\s]+)\s+in\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input, re.IGNORECASE)
        if sched_open_orig:
            app_name = sched_open_orig.group(1).strip()
            val_val = int(sched_open_orig.group(2).strip())
            unit_val = sched_open_orig.group(3).strip().lower()
            
            multiplier = 1
            if unit_val.startswith("m"):
                multiplier = 60
            elif unit_val.startswith("h"):
                multiplier = 3600
                
            trigger_time = time.time() + (val_val * multiplier)
            res = add_jarvis_schedule("one-shot", trigger_time, f"open {app_name}")
            print(f"\n{res}")
            return

    # Close app relative: close chrome in 10 minutes
    sched_close_match = re.match(r'^close\s+([a-zA-Z0-9_\-\.\s]+)\s+in\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input_lower)
    if sched_close_match:
        sched_close_orig = re.match(r'^close\s+([a-zA-Z0-9_\-\.\s]+)\s+in\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input, re.IGNORECASE)
        if sched_close_orig:
            app_name = sched_close_orig.group(1).strip()
            val_val = int(sched_close_orig.group(2).strip())
            unit_val = sched_close_orig.group(3).strip().lower()
            
            multiplier = 1
            if unit_val.startswith("m"):
                multiplier = 60
            elif unit_val.startswith("h"):
                multiplier = 3600
                
            trigger_time = time.time() + (val_val * multiplier)
            res = add_jarvis_schedule("one-shot", trigger_time, f"close {app_name}")
            print(f"\n{res}")
            return

    # Open app absolute: open chrome at 10:00
    sched_open_abs = re.match(r'^open\s+([a-zA-Z0-9_\-\.\s]+)\s+at\s+(\d{1,2}:\d{2})$', user_input_lower)
    if sched_open_abs:
        sched_open_abs_orig = re.match(r'^open\s+([a-zA-Z0-9_\-\.\s]+)\s+at\s+(\d{1,2}:\d{2})$', user_input, re.IGNORECASE)
        if sched_open_abs_orig:
            app_name = sched_open_abs_orig.group(1).strip()
            time_val = sched_open_abs_orig.group(2).strip()
            if len(time_val.split(":")[0]) == 1:
                time_val = "0" + time_val
            now_dt = datetime.datetime.now()
            target_dt_str = f"{now_dt.strftime('%Y-%m-%d')} {time_val}:00"
            target_dt = datetime.datetime.strptime(target_dt_str, "%Y-%m-%d %H:%M:%S")
            if now_dt > target_dt:
                target_dt += datetime.timedelta(days=1)
                target_dt_str = target_dt.strftime("%Y-%m-%d %H:%M:%S")
            res = add_jarvis_schedule("one-shot", target_dt_str, f"open {app_name}")
            print(f"\n{res}")
            return

    # Close app absolute: close chrome at 18:00
    sched_close_abs = re.match(r'^close\s+([a-zA-Z0-9_\-\.\s]+)\s+at\s+(\d{1,2}:\d{2})$', user_input_lower)
    if sched_close_abs:
        sched_close_abs_orig = re.match(r'^close\s+([a-zA-Z0-9_\-\.\s]+)\s+at\s+(\d{1,2}:\d{2})$', user_input, re.IGNORECASE)
        if sched_close_abs_orig:
            app_name = sched_close_abs_orig.group(1).strip()
            time_val = sched_close_abs_orig.group(2).strip()
            if len(time_val.split(":")[0]) == 1:
                time_val = "0" + time_val
            now_dt = datetime.datetime.now()
            target_dt_str = f"{now_dt.strftime('%Y-%m-%d')} {time_val}:00"
            target_dt = datetime.datetime.strptime(target_dt_str, "%Y-%m-%d %H:%M:%S")
            if now_dt > target_dt:
                target_dt += datetime.timedelta(days=1)
                target_dt_str = target_dt.strftime("%Y-%m-%d %H:%M:%S")
            res = add_jarvis_schedule("one-shot", target_dt_str, f"close {app_name}")
            print(f"\n{res}")
            return

    # Open app recurring: open chrome every 30 minutes
    sched_open_rec = re.match(r'^open\s+([a-zA-Z0-9_\-\.\s]+)\s+every\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input_lower)
    if sched_open_rec:
        sched_open_rec_orig = re.match(r'^open\s+([a-zA-Z0-9_\-\.\s]+)\s+every\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input, re.IGNORECASE)
        if sched_open_rec_orig:
            app_name = sched_open_rec_orig.group(1).strip()
            val_val = int(sched_open_rec_orig.group(2).strip())
            unit_val = sched_open_rec_orig.group(3).strip().lower()
            
            if unit_val.startswith("s"):
                mins_val = val_val / 60.0
            elif unit_val.startswith("h"):
                mins_val = val_val * 60
            else:
                mins_val = val_val
                
            res = add_jarvis_schedule("recurring", None, f"open {app_name}", interval_mins=mins_val)
            print(f"\n{res}")
            return

    # Close app recurring: close chrome every 30 minutes
    sched_close_rec = re.match(r'^close\s+([a-zA-Z0-9_\-\.\s]+)\s+every\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input_lower)
    if sched_close_rec:
        sched_close_rec_orig = re.match(r'^close\s+([a-zA-Z0-9_\-\.\s]+)\s+every\s+(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$', user_input, re.IGNORECASE)
        if sched_close_rec_orig:
            app_name = sched_close_rec_orig.group(1).strip()
            val_val = int(sched_close_rec_orig.group(2).strip())
            unit_val = sched_close_rec_orig.group(3).strip().lower()
            
            if unit_val.startswith("s"):
                mins_val = val_val / 60.0
            elif unit_val.startswith("h"):
                mins_val = val_val * 60
            else:
                mins_val = val_val
                
            res = add_jarvis_schedule("recurring", None, f"close {app_name}", interval_mins=mins_val)
            print(f"\n{res}")
            return

    # 5.5 Battery diagnostics
    if re.match(r'^(battery|battery\s+status|power\s+status|power\s+diagnostics)$', user_input_lower):
        res = get_battery_status()
        print(f"\n{res}")
        return

    # 5.6 Power Controls
    power_match = re.match(r'^(sleep|restart|shutdown)\s+pc$', user_input_lower)
    if power_match:
        state = power_match.group(1)
        res = set_power_state(state)
        print(f"\n{res}")
        return

    # 5.7 Keep Awake Anti-Lock / Jiggler
    if re.match(r'^(keep\s+awake|jiggle\s+mouse|start\s+jiggle)$', user_input_lower):
        res = start_keep_awake()
        print(f"\n{res}")
        return
    if re.match(r'^(stop\s+awake|stop\s+jiggle|disable\s+jiggle)$', user_input_lower):
        res = stop_keep_awake()
        print(f"\n{res}")
        return

    # 5.8 Brightness Controls
    brightness_match = re.match(r'^brightness\s+(\d+)$', user_input_lower)
    if brightness_match:
        level = brightness_match.group(1)
        res = set_brightness(level)
        print(f"\n{res}")
        return

    # 5.9 Media Playback Controls
    media_match = re.match(r'^(play|pause|next\s+song|skip|previous\s+song|next|prev|previous)$', user_input_lower)
    if media_match:
        cmd = media_match.group(1)
        if "next" in cmd or cmd == "skip":
            cmd_norm = "next"
        elif "prev" in cmd:
            cmd_norm = "previous"
        else:
            cmd_norm = cmd
        res = trigger_media_key(cmd_norm)
        print(f"\n{res}")
        return

    # 6. Open Application
    open_match = re.match(r'^open\s+([a-zA-Z0-9_\-\.\s]+)$', user_input_lower)
    if open_match:
        app_name = open_match.group(1).strip()
        # Edge case: "open website ..."
        if app_name.startswith("website "):
            url = app_name[len("website "):].strip()
            res = open_url(url)
            print(f"\n{res}")
            return
        res = open_app(app_name)
        print(f"\n{res}")
        return

    # 6.4 Close Current App
    if re.match(r'^(close\s+current\s+app|close\s+current\s+window|close\s+active\s+app|close\s+current)$', user_input_lower):
        res = close_current_app()
        print(f"\n{res}")
        return

    # 6.45 Minimize/Maximize Controls
    if re.match(r'^(minimize\s+all|minimize\s+all\s+apps|minimize\s+all\s+windows)$', user_input_lower):
        res = minimize_all()
        print(f"\n{res}")
        return
        
    if re.match(r'^(maximize\s+all|maximize\s+all\s+apps|maximize\s+all\s+windows|restore\s+all|restore\s+all\s+apps|restore\s+all\s+windows)$', user_input_lower):
        res = maximize_all()
        print(f"\n{res}")
        return

    if re.match(r'^(minimize\s+current\s+app|minimize\s+current\s+window|minimize\s+active\s+app|minimize\s+current)$', user_input_lower):
        res = minimize_current_app()
        print(f"\n{res}")
        return

    if re.match(r'^(maximize\s+current\s+app|maximize\s+current\s+window|maximize\s+active\s+app|maximize\s+current|restore\s+current\s+app)$', user_input_lower):
        res = maximize_current_app()
        print(f"\n{res}")
        return

    # 6.47 Maximize/Minimize Specific App
    maximize_match = re.match(r'^maximize\s+([a-zA-Z0-9_\-\.\s]+)$', user_input_lower)
    if maximize_match:
        app_name = maximize_match.group(1).strip()
        res = maximize_app(app_name)
        print(f"\n{res}")
        return

    minimize_app_match = re.match(r'^minimize\s+([a-zA-Z0-9_\-\.\s]+)$', user_input_lower)
    if minimize_app_match:
        app_name = minimize_app_match.group(1).strip()
        res = minimize_app(app_name)
        print(f"\n{res}")
        return

    # 6.49 Window Layout & Snapping
    snap_match = re.match(r'^snap\s+([a-zA-Z0-9_\-\.\s]+)\s+(left|right|top|bottom|maximize|minimize|max|min)$', user_input_lower)
    if snap_match:
        app_name = snap_match.group(1).strip()
        direction = snap_match.group(2).strip()
        res = snap_app(app_name, direction)
        print(f"\n{res}")
        return

    # 6.51 Smart App Switching
    switch_match = re.match(r'^(?:switch\s+to\s+|focus\s+)([a-zA-Z0-9_\-\.\s]+)$', user_input_lower)
    if switch_match:
        app_name = switch_match.group(1).strip()
        res = switch_to_app(app_name)
        print(f"\n{res}")
        return

    # 6.52 App Volume Control
    # Mute controls
    if user_input_lower in ["mute", "mute master", "mute pc", "mute system", "mute speaker", "mute speakers"]:
        res = control_volume("master", "mute")
        print(f"\n{res}")
        return
    vol_mute_match = re.match(r'^mute\s+([a-zA-Z0-9_\-\.\s]+)$', user_input_lower)
    if vol_mute_match:
        app_name = vol_mute_match.group(1).strip()
        res = control_volume(app_name, "mute")
        print(f"\n{res}")
        return

    # Unmute controls
    if user_input_lower in ["unmute", "unmute master", "unmute pc", "unmute system", "unmute speaker", "unmute speakers"]:
        res = control_volume("master", "unmute")
        print(f"\n{res}")
        return
    vol_unmute_match = re.match(r'^unmute\s+([a-zA-Z0-9_\-\.\s]+)$', user_input_lower)
    if vol_unmute_match:
        app_name = vol_unmute_match.group(1).strip()
        res = control_volume(app_name, "unmute")
        print(f"\n{res}")
        return

    # Volume Up/Down relative adjustments
    if user_input_lower in ["volume up", "vol up"]:
        res = control_volume("master", "up")
        print(f"\n{res}")
        return
    if user_input_lower in ["volume down", "vol down"]:
        res = control_volume("master", "down")
        print(f"\n{res}")
        return
    vol_updown_match = re.match(r'^volume\s+([a-zA-Z0-9_\-\.\s]+)\s+(up|down)$', user_input_lower)
    if vol_updown_match:
        app_name = vol_updown_match.group(1).strip()
        action = vol_updown_match.group(2).strip()
        res = control_volume(app_name, action)
        print(f"\n{res}")
        return

    # Volume Absolute Sets
    vol_set_master_match = re.match(r'^volume\s+(\d+)$', user_input_lower)
    if vol_set_master_match:
        level = int(vol_set_master_match.group(1).strip())
        res = control_volume("master", "set", level)
        print(f"\n{res}")
        return
    vol_set_match = re.match(r'^volume\s+([a-zA-Z0-9_\-\.\s]+)\s+(\d+)$', user_input_lower)
    if vol_set_match:
        app_name = vol_set_match.group(1).strip()
        level = int(vol_set_match.group(2).strip())
        if app_name in ["master", "pc", "system", "all", "speaker", "speakers"]:
            res = control_volume("master", "set", level)
        else:
            res = control_volume(app_name, "set", level)
        print(f"\n{res}")
        return

    # 6.5 Close Application
    close_match = re.match(r'^close\s+([a-zA-Z0-9_\-\.\s]+)$', user_input_lower)
    if close_match:
        app_name = close_match.group(1).strip()
        res = close_app(app_name)
        print(f"\n{res}")
        return

    # 7. Open Website
    web_match = re.match(r'^(?:open\s+)?website\s+(.+)$', user_input_lower)
    if web_match:
        url = web_match.group(1).strip()
        res = open_url(url)
        print(f"\n{res}")
        return

    # 8. Web Search
    search_match = re.match(r'^search\s+(.+)$', user_input_lower)
    if search_match:
        query = search_match.group(1).strip()
        res = search_web(query)
        print(f"\n{res}")
        return

    # 9. Run Command
    cmd_match = re.match(r'^(?:run|cmd|exec)\s+(.+)$', user_input_lower)
    if cmd_match:
        # Preserve shell casing by matching original user input
        match_orig = re.match(r'^(?:run|cmd|exec)\s+(.+)$', user_input, re.IGNORECASE)
        if match_orig:
            command_to_run = match_orig.group(1).strip()
            res = run_shell_command(command_to_run)
            print(f"\n{res}")
            return

    # 10. Fallback / Fuzzy Suggestion
    import difflib
    PRIMARY_COMMANDS = [
        "status", "battery", "lock pc", "sleep pc", "restart pc", "shutdown pc",
        "clean temp", "empty trash", "turn off screen", "dark mode", "light mode",
        "top processes", "idle time", "disk check", "storage", "optimize memory",
        "calendar", "time", "date", "open", "close", "kill pid", "copy path",
        "schedule", "schedules", "list schedules", "cancel schedule", "alarm",
        "snap", "switch to", "focus", "minimize", "maximize", "minimize current",
        "maximize current", "minimize all", "maximize all", "new desktop",
        "close desktop", "next desktop", "prev desktop", "previous desktop",
        "brightness", "keep awake", "stop awake", "volume", "mute", "unmute",
        "play", "pause", "next", "skip", "previous", "mute mic", "unmute mic",
        "volume status", "wifi signal", "screenshot", "clear clipboard",
        "whatsapp login", "whatsapp message", "whatsapp send file", "whatsapp unreads",
        "whatsapp auto-reply", "whatsapp read last", "whatsapp status of",
        "whatsapp call", "whatsapp video call", "whatsapp broadcast", "whatsapp mute",
        "whatsapp unmute", "whatsapp logout", "website", "search", "help"
    ]
    
    # Fuzzy match the entire input
    matches = difflib.get_close_matches(user_input_lower, PRIMARY_COMMANDS, n=1, cutoff=0.6)
    if matches:
        print(f"\n{COLOR_CYAN}[JARVIS]: Command not recognized. Did you mean: '{matches[0]}'?{COLOR_RESET}")
    else:
        # Check first word
        words = user_input_lower.split()
        if words:
            first_word = words[0]
            kw_matches = difflib.get_close_matches(first_word, PRIMARY_COMMANDS, n=1, cutoff=0.6)
            if kw_matches:
                print(f"\n{COLOR_CYAN}[JARVIS]: Command not recognized. Did you mean: '{kw_matches[0]}'?{COLOR_RESET}")
            else:
                print(f"\n{COLOR_CYAN}[JARVIS]: Command not recognized under standard protocol. Type 'help' to view the options.{COLOR_RESET}")
        else:
            print(f"\n{COLOR_CYAN}[JARVIS]: Command not recognized under standard protocol. Type 'help' to view the options.{COLOR_RESET}")

def start_hotkey_listener():
    import threading
    
    def hotkey_thread_func():
        import ctypes
        import ctypes.wintypes
        
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        MODIFIERS = 0x0002 | 0x0001  # MOD_CONTROL (0x02) | MOD_ALT (0x01)
        VK_J = 0x4A                  # 'J' key
        HOTKEY_ID = 42
        
        res = user32.RegisterHotKey(None, HOTKEY_ID, MODIFIERS, VK_J)
        if not res:
            return
            
        try:
            msg = ctypes.wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312:  # WM_HOTKEY
                    if msg.wParam == HOTKEY_ID:
                        hwnd = kernel32.GetConsoleWindow()
                        if hwnd:
                            # SW_RESTORE = 9
                            user32.ShowWindow(hwnd, 9)
                            user32.SetForegroundWindow(hwnd)
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, HOTKEY_ID)
            
    thread = threading.Thread(target=hotkey_thread_func, daemon=True)
    thread.start()

def focus_existing_jarvis():
    import ctypes
    import ctypes.wintypes
    
    user32 = ctypes.windll.user32
    
    # Callback type
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    
    hwnd_list = []
    
    def get_window_title(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            return buffer.value
        return ""

    def enum_windows_callback(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            title = get_window_title(hwnd)
            if "Jarvis Assistant" in title:
                hwnd_list.append(hwnd)
        return True
        
    cb = WNDENUMPROC(enum_windows_callback)
    user32.EnumWindows(cb, 0)
    
    # Focus the first match that is NOT current console
    current_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    for hwnd in hwnd_list:
        if hwnd != current_hwnd:
            user32.ShowWindow(hwnd, 9) # SW_RESTORE = 9
            user32.SetForegroundWindow(hwnd)
            break

def enable_colors():
    import sys
    import ctypes
    if sys.platform != "win32":
        return True
    kernel32 = ctypes.windll.kernel32
    hStdOut = kernel32.GetStdHandle(-11) # STD_OUTPUT_HANDLE
    if hStdOut == -1 or hStdOut is None:
        return False
    mode = ctypes.c_ulong()
    if kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode)):
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        return bool(kernel32.SetConsoleMode(hStdOut, mode.value | 0x0004))
    return False

def main():
    import ctypes
    enable_colors()
    
    MUTEX_NAME = "Global\\JarvisAssistantUniqueMutexName"
    
    global _instance_mutex
    _instance_mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        focus_existing_jarvis()
        sys.exit(0)

    print(BANNER)
    speak("Hello sir.")
    
    # Start the global hotkey listener in background
    start_hotkey_listener()
    
    # Start the background task scheduler
    from schedule.scheduler import scheduler_loop
    threading.Thread(target=scheduler_loop, args=(parse_and_execute,), daemon=True).start()
    
    # Start the always-listening loop in main thread
    from voice_engine import always_listening_loop
    always_listening_loop()

if __name__ == "__main__":
    main()
