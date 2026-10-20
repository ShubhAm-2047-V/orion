import os
import sys
try:
    import win32com.client
except ImportError:
    win32com = None

def create_desktop_shortcut(hotkey="Ctrl+Alt+B", icon_index=24):
    desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
    shortcut_path = os.path.join(desktop_dir, "Jarvis.lnk")
    
    if win32com is None:
        print("[ERROR]: pywin32 module is required to create Windows shortcuts.")
        return False

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = r"e:\orion\run.bat"
    shortcut.WorkingDirectory = r"e:\orion"
    shortcut.Hotkey = hotkey
    # Set a premium computer/terminal icon from shell32.dll (index 24 is cmd/window icon, index 23 is PC icon)
    shortcut.IconLocation = f"C:\\Windows\\System32\\shell32.dll, {icon_index}"
    shortcut.Description = "Launch JARVIS AI OS Assistant & Dashboard Control Center"
    shortcut.Save()
    print(f"[JARVIS]: Shortcut updated successfully at: {shortcut_path} (Hotkey: {hotkey})")
    return True

if __name__ == "__main__":
    create_desktop_shortcut()
