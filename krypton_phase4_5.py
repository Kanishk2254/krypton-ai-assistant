import speech_recognition as sr
import pyttsx3
import json
import difflib
import subprocess
import datetime
import getpass
import os
import pygame
import re
import sys
import threading
import time
import pystray
from PIL import Image
import spacy
import traceback
import importlib.util
from plyer import notification
from cryptography.fernet import Fernet
from core.context_manager import context_manager
from core.nlp_engine import create_nlp_engine

# Load settings
with open("settings.json", "r") as f:
    settings = json.load(f)

ASSISTANT_NAME = settings["assistant_name"]
USER_NAME = settings["user_name"]
VOICE_MODE = settings["voice_mode"]
CONFIRM_SOUND = settings["confirm_sound"]
ERROR_SOUND = settings["error_sound"]
LOG_COMMANDS = settings["log_commands"]
TRIGGER_PHRASES = settings["trigger_phrases"]
DEFAULT_BROWSER = settings["default_browser"]
TRAY_ICON_PATH = settings["tray_icon"]
DEBUG_MODE = settings["debug_mode"]
SILENT_MODE = False

# Global variables
SESSION_ACTIVE = True
LOG_FILE = "command_log.txt"
# Security PIN from environment variable (more secure)
SECURITY_PIN = os.getenv("KRYPTON_PIN", "1234")  # Default: 1234
last_command_context = None
REMINDER_FILE = "reminders.json"
custom_plugin = []

# Update settings
def update_settings_json():
    try:
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=2)
        if settings.get("debug_mode"):
            print("[Debug] settings.json updated.")
    except Exception as e:
        print(f"[ERROR] Failed to update settings.json: {e}")

# Load tray configuration
with open("tray_icon_config.json", "r") as f:
    tray_config = json.load(f)

tray_icon = None

# Load enhanced NLP with context awareness
nlp_engine = create_nlp_engine(context_manager)

# Load spaCy model for basic NLP
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    print("[WARNING] spaCy model not available. Some NLP features disabled.")
    nlp = None

# Initialize engine
engine = pyttsx3.init()
pygame.mixer.init()

# Wake phrase
def detect_wake_phrase(command):
    triggers = ["hey krypton", "wake up", "awaken", "arise", "rise krypton", "initiate sequence"]
    return any(trigger in command.lower() for trigger in triggers)

# play feedback
def play_feedback(filename):
    path = os.path.join("sounds", filename)
    if os.path.exists(path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

# Command config
with open("commands_config.json", "r") as f:
    commands_config = json.load(f)

ALIASES = {}
for command, config in commands_config.items():
    if isinstance(config, list):
        for alias in config:
            ALIASES[alias.lower()] = command
    elif isinstance(config, dict):
        for alias in config.get("aliases", []):
            ALIASES[alias.lower()] = command

# Listen command
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening....")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {command}")
        return command.lower() #type: ignore
    except sr.UnknownValueError:
        play_feedback(ERROR_SOUND)
        speak("Sorry, I couldn't catch that.")
    except sr.RequestError:
        play_feedback(ERROR_SOUND)
        speak("Network Error.")
    return ""

# Basic NLP intent extractor
def parse_nlp_command(text):
    if nlp is None:
        return None
    doc = nlp(text)
    for token in doc:
        if token.lemma_ in ALIASES:
            return ALIASES[token.lemma_]
    return None

# Verify PIN
def verify_security_pin():
    voice_attempt = listen_command()
    if SECURITY_PIN in voice_attempt:
        play_feedback(CONFIRM_SOUND)
        return True
    else:
        speak("Voice PIN incorrect. Enter Manually.")
        manual = getpass.getpass("Enter PIN: ")
        return manual == SECURITY_PIN

# Logging
def log_command(cmd):
    if settings["log_commands"]:
        with open("command_log.txt", "a") as log:
            log.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')} - {cmd}\n")

# Command context memory
command_context = {
    "last_command": None,
    "last_param": None,
}

def update_context(command, param):
    command_context["last_command"] = command
    command_context["last_param"] = param

# Help commad
def show_help():
    speak("Here are some things you can ask me to do:")
    for cmd, cfg in commands_config.items():
        examples = cfg.get("aliases", [])
        if examples:
            print(f"🔹 {cmd}: {', '.join(examples[:2])}")
    speak("You can say'open notepad', 'gettime', or 'search for something on google'.")

# Reminder system
if not os.path.exists(REMINDER_FILE):
    with open(REMINDER_FILE, "w") as f:
        json.dump([], f, indent=2)

# Reminder system
def set_reminder(text):
    now = datetime.datetime.now()
    
    match = re.search(r"remind me to (.+?) in (\d+) (second|seconds|minute|minutes)", text)
    if match:
        task, amount, unit = match.groups()
        delay = int(amount) * (60 if "minute" in unit else 1)
        due_time = (now + datetime.timedelta(seconds=delay)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        match = re.search(r"remind me to (.+?) at (\d{1,2}:\d{2}(?:\s?[ap]m)?)", text)
        if match:
            task, time_str = match.groups()
            try:
                due = datetime.datetime.strptime(time_str.strip().lower(), "%I:%M%p")
                due = due.replace(year=now.year, month=now.month, day=now.day)
                if due < now:
                    due += datetime.timedelta(days=1)
                due_time = due.strftime("%Y-%m-%d %H:%M:%S")
            except:
                speak("Couldn't parse the time format.")
                return
        else:
            speak("Sorry, I couldn't understand the reminder format.")
            return
    
    with open(REMINDER_FILE, "r+") as f:
        reminders = json.load(f)
        reminders.append({"task": task, "due": due_time, "notified": False})
        f.seek(0)
        json.dump(reminders, f, indent=2)
    
    speak(f"Reminder set for '{task}' at '{due_time}'")

def check_reminder_loop():
    while True:
        now = datetime.datetime.now()
        with open(REMINDER_FILE, "r+") as f:
            reminders = json.load(f)
            for reminder in reminders:
                if not reminder["notified"]:
                    due = datetime.datetime.strptime(reminder["due"], "%Y-%m-%d %H:%M:%S")
                    if now >= due:
                        notification.notify(
                            title="🔔 Reminder from KRYPTON",
                            message=reminder["task"],
                            timeout=5) # type: ignore
                        speak(f"⏰ Reminder: {reminder['task']}")
                        reminder["notified"] = True
            f.seek(0)
            json.dump(reminders, f, indent=2)
        time.sleep(30)
    
# Match fuzzy command
def match_command(user_input):
    matches = difflib.get_close_matches(user_input, ALIASES.keys(), n=1, cutoff=0.6)
    return ALIASES[matches[0]] if matches else None

# Extract dynamic parameter
def extract_parameter(text, pattern):
    match = re.search(pattern, text)
    return match.group(1) if match else ""

# Sensitive action
def confirm_sensitive():
    speak("This is a sensitive action. Proceed?")
    return "yes" in listen_command()

# Tray icon
def update_tray_icon():
    global tray_icon
    if not tray_icon:
        return
    try:
        icon_path = tray_config["voice_on_icon"] if VOICE_MODE else tray_config["voice_off_icon"]
        tray_icon.icon = Image.open(icon_path)
    except Exception as e:
        print(f"[Tray Icon] Failed to update tray icon: {e}")

def create_tray_icon():
    def on_quit(icon, item):
        speak("Exiting from tray.")
        icon.stop()
        sys.exit()
    
    def on_toggle(icon, item):
        global VOICE_MODE
        VOICE_MODE = not VOICE_MODE
        speak(f"Voice Mode {'on' if VOICE_MODE else 'off'}")
        update_tray_icon()
    
    try:
        icon_image = Image.open(tray_config["default_icon"])
    except Exception as e:
        print(f"[Tray Icon] Failed to load default icon: {e}")
        return
    
    menu = pystray.Menu(
        pystray.MenuItem("Toggle Voice Mode", on_toggle),
        pystray.MenuItem("Quit", on_quit)
    )
    
    global tray_icon
    tray_icon = pystray.Icon("krypton", icon_image, "KRYPTON", menu)
    tray_icon.run()

# System sound control
def control_volume(action):
    if action == "mute":
        subprocess.run("nircmd.exe mutesysvolume 1", shell=True)
        speak("System Muted.")
    elif action == "unmute":
        subprocess.run("nircmd.exe mutesysvolume 0", shell=True)
        speak("System Unmuted.")
    elif action.startswith("volume"):
        level = extract_parameter(action, r"volume (\d+)")
        if level:
            subprocess.run(f"nircmd.exe setsysvolume {int(int(level) * 655.35)}", shell=True)
            speak(f"Volume set to {level} percent.")


# NLP parsing
def nlp_parse(user_input):
    if "mute" in user_input:
        return "mute_audio"
    if "unmute" in user_input:
        return "unmute_audio"
    if "volume" in user_input:
        return "set_volume"
    return None

# NLP Action Route
def handle_nlp_command(parse_cmd, raw_input):
    if parse_cmd == "mute_audio":
        control_volume("mute")
    elif parse_cmd == "unmute_audio":
        control_volume("unmute")
    elif parse_cmd == "set_volume":
        control_volume(raw_input)

# Load plugins
def load_plugins():
    global custom_plugin
    plugins_dir = "plugins"
    
    if not os.path.isdir(plugins_dir):
        os.makedirs(plugins_dir)
        
    custom_plugin = []
    
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py"):
            command_name = os.path.splitext(filename)[0]
            custom_plugin.append(command_name)
            print(f"Loaded Plugin: {filename}")

# Execute plugin (with security restrictions)
def exec_plugin(command, user_input):
    plugin_path = os.path.join("plugins", f"{command}.py")
    if not os.path.isfile(plugin_path):
        speak(f"The plugin for {command} was not found.")
        return
    
    try:
        with open(plugin_path,"r") as f:
            plugin_code = f.read()
        
        # Security: Check for dangerous operations
        dangerous_keywords = ['import os', 'import sys', 'subprocess', 'eval(', 'exec(', '__import__']
        if any(keyword in plugin_code for keyword in dangerous_keywords):
            speak("Security warning: Plugin contains potentially dangerous operations.")
            if not confirm_sensitive():
                speak("Plugin execution cancelled for security.")
                return
            
        # Restricted execution environment
        exec(plugin_code, {
            '__builtins__': {'print': print, 'len': len, 'str': str, 'int': int, 'float': float},
            'input_text': user_input,
            'speak': speak,
            'VOICE_MODE': VOICE_MODE,
            'settings': settings,
            'play_feedback': play_feedback})
        
    except Exception as e:
        print(f"[ERROR] Plugin execution failed: {e}")
        if settings.get("debug_mode"):
            traceback.print_exc()
        speak("Failed to execute plugin.")
        
    
# Load debug mode setting from config
DEBUG_MODE = settings.get("debug_mode", False)

def debug_log(message):
    if DEBUG_MODE:
        print(f"[DEBUG]: {message}")

# Toggle silent mode
def toggle_silent_mode():
    global SILENT_MODE
    SILENT_MODE = not SILENT_MODE
    speak(f"Silent mode {'enabled' if SILENT_MODE else 'disabled'}.")

# Replace speak if silent
def speak(text):
    if VOICE_MODE and not SILENT_MODE:
        engine.say(text)
        engine.runAndWait()
    if not SILENT_MODE:
        print(f"[{ASSISTANT_NAME}]: {text}")

# Session timeout
SESSION_TIMEOUT = 300 # 5 minutes
last_activity_time = time.time()

def reset_activity_timer():
    global last_activity_time
    last_activity_time = time.time()

def check_session_timeout():
    while True:
        if time.time() - last_activity_time > SESSION_TIMEOUT:
            speak("Session expired. Re-authentication required.")
            if not verify_security_pin():
                speak("Authentication Failed. Shutting Down.")
                sys.exit()
            speak("Session re-activated.")
            reset_activity_timer()
        time.sleep(10)
# Start session checker thread
timeout_thread = threading.Thread(target=check_session_timeout, daemon=True)
timeout_thread.start()

# Load encryption key
KEY_FILE = "secure_log.txt"
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(Fernet.generate_key())

with open(KEY_FILE, "rb") as f:
    LOG_KEY = f.read()

fernet = Fernet(LOG_KEY)

def log_encrypted_command(cmd):
    if settings.get("log_commands",True):
        encrypted = fernet.encrypt(cmd.encode())
        with open("encrypted_log.bin", "ab") as log:
            log.write(encrypted + b"\n")

# Execute command with enhanced context tracking
def execute_command(command, input_text):
    global VOICE_MODE
    log_command(input_text)
    
    # Process input with enhanced NLP
    nlp_result = nlp_engine.process_input(input_text)
    
    # Add to context memory
    context_manager.add_command_to_context(
        command=command,
        input_text=input_text,
        entities=nlp_result.get("entities", {})
    )
    
    # Basic commands
    if command == "open_notepad":
        subprocess.Popen(["notepad.exe"])
        
    elif command == "open_chrome":
        subprocess.Popen(["start", "chrome"], shell=True)
        
    elif command == "get_time":
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        speak(f"The current time is {current_time}.")
        
    elif command == "search_web":
        query = extract_parameter(input_text, r"(?:search|google|find) (.+)")
        if query:
            subprocess.Popen(["start", f"https://www.google.com/search?q={query}"])
        else:
            speak("What should I search?")
            
    elif command == "open_file":
        filename = extract_parameter(input_text, r"open file (.+)")
        if os.path.exists(filename):
            os.startfile(filename)
        else:
            play_feedback(settings["error_sound"])
            speak("File not found.")
    
    # Voice Controls
    elif command == "voice_on":
        VOICE_MODE = True
        speak("Voice Mode activated.")
        update_tray_icon()
        update_settings_json()
    
    elif command == "voice_off":
        VOICE_MODE = False
        speak("Voice mode deactivated.")
        update_tray_icon()
        update_settings_json()
    
    elif command == "mute_sound":
        subprocess.run(["nircmd.exe", "mutesysvolume", "1"])
        speak("System sound muted.")
    
    elif command == "unmute_sound":
        subprocess.run(["nircmd.exe", "mutesysvolume", "0"])
        speak("System sound unmuted.")
    
    elif command == "increase_volume":
        subprocess.run(["nircmd.exe", "changesysvolume", "5000"])
        speak("Volume Increased.")
    
    elif command == "decrease_volume":
        subprocess.run(["nircmd.exe", "changesysvolume", "-5000"])
        speak("Volume Decreased.")
    
    # Reminder
    elif "remind me" in input_text:
        set_reminder(input_text)
    
    # Developer mode toggle
    elif command == "toggle_debug":
        settings["debug_mode"] = not settings["debug_mode"]
        speak(f"Debug mode {'enabled' if settings['debug_mode'] else 'disabled'}.")
        update_settings_json()
    
    # Plugin commads
    elif command in custom_plugin:
        exec_plugin(command, input_text)
    
    # Exit
    elif command == "exit":
        speak("Shutting down. Goodbye.")
        sys.exit()
    
    # NLP
    elif settings.get("nlp_enabled", True):
        parsed = nlp(input_text) # type: ignore
        speak("I recognized your request but need more context.")
    
    else:
        speak("This command is not implemented yet.")


# Enhanced main loop with NLP and context awareness
def main_loop():
    global VOICE_MODE
    speak("KRYPTON phase 4.5 online with enhanced intelligence.")
    
    while True:
        user_input = listen_command()
        if not user_input:
            continue
        
        # Process with enhanced NLP first
        nlp_result = nlp_engine.process_input(user_input)
        
        # Handle voice mode toggles
        if "activate voice mode" in user_input:
            VOICE_MODE = True
            speak("Voice mode activated.")
            continue
        elif "deactivate voice mode" in user_input:
            VOICE_MODE = False
            speak("🔇 Voice mode deactivated.")
            continue
        
        # Try NLP-based intent detection first
        if nlp_result["intent"] != "unknown" and nlp_result["confidence"] > 0.6:
            command_key = nlp_result["intent"]
            if DEBUG_MODE:
                print(f"[NLP] Detected intent: {command_key} (confidence: {nlp_result['confidence']:.2f})")
        else:
            # Fallback to fuzzy matching
            command_key = match_command(user_input)
        
        if command_key:
            config = commands_config.get(command_key)
            if isinstance(config, dict) and config.get("sensitive"):
                if not confirm_sensitive():
                    speak("Action cancelled")
                    continue
            
            play_feedback(CONFIRM_SOUND)
            
            # Execute with enhanced context
            try:
                execute_command(command_key, user_input)
                
                # Provide contextual feedback
                if nlp_result.get("context_resolved"):
                    speak("I understood your reference.")
                    
            except Exception as e:
                if DEBUG_MODE:
                    print(f"[ERROR] Command execution failed: {e}")
                speak("There was an error executing that command.")
                play_feedback(ERROR_SOUND)
                
        else:
            play_feedback(ERROR_SOUND)
            
            # Provide intelligent suggestions
            suggestions = nlp_result.get("suggestions", [])
            if suggestions:
                speak(f"I didn't understand that. {suggestions[0]}")
            else:
                speak("Sorry, I didn't catch that command. Try saying 'help' for available commands.")

# Start
if __name__ == "__main__":
    speak("KRYPTON initialized and secured. Awaiting authentication.")
    if not verify_security_pin():
        speak("Authentication failed. Shutting down.")
        sys.exit()
    
    speak("Authentication Successful.")
    speak("Speaketh the ancient phrase to proveth thou art worthy")

    while True:
        # Wait for wake phrase
        if detect_wake_phrase(listen_command()):
            play_feedback(CONFIRM_SOUND)
            break

    # Start tray icon ONLY after wake phrase
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

    # Start the main command loop
    main_loop()
