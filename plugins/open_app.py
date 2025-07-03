import subprocess
import re
import os
import winreg

APP_PATHS = {
    "notepad": "notepad.exe",
    "discord": r"C:\Users\Kanishk\AppData\Local\Discord\Update.exe --processStart Discord.exe",
    "spotify": r"C:\Users\Kanishk\AppData\Roaming\Spotify\Spotify.exe",
    "vs code": r"C:\Users\Kanishk\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe"
}

for key in APP_PATHS:
    APP_PATHS[key] = os.path.expandvars(APP_PATHS[key])

def discover_app_paths(app_name):
    try:
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"
        ]
        for reg_path in registry_paths:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    if app_name.lower() in subkey_name.lower():
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            value, _ = winreg.QueryValueEx(subkey, "")
                            return value
    except Exception as e:
        print(f"[DEBUG] Registry lookup failed: {e}")
    return None

# Parse user input
text = input_text.lower()
match = re.search(r"(?:open|launch|start|run)\s+(.+)", text)

if match:
    app_name = match.group(1).strip()

    # Check predefined list
    for name, path in APP_PATHS.items():
        if name in app_name:
            try:
                subprocess.Popen(path, shell=True)
                speak(f"Opening {name}")
            except Exception as e:
                speak(f"Failed to open {name}.")
                print(f"[ERROR] {e}")
            break
    else:
        # Attempt registry auto-discovery
        discovered = discover_app_paths(app_name)
        if discovered:
            subprocess.Popen(discovered, shell=True)
            speak(f"Discovered and opened {app_name}")
        else:
            speak("Sorry, I couldn't find that application.")
else:
    speak("Please tell me what to open.")