import re
import os
import pygame
import webbrowser

MUSIC_DIR = "Music"

if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)

if not pygame.mixer.get_init():
    pygame.mixer.init()

# GLOBALS
if 'music_queue' not in globals():
    music_queue = []
    current_index = 0
    paused = False

def list_music():
    return [f for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.wav'))]

def add_to_queue(song_name):
    files = list_music()
    for file in files:
        if song_name.lower() in file.lower():
            music_queue.append(os.path.join(MUSIC_DIR, file))
            return file
    return None

def play_next():
    global current_index
    if current_index < len(music_queue):
        pygame.mixer.music.load(music_queue[current_index])
        pygame.mixer.music.play()
        speak(f"Now playing {os.path.basename(music_queue[current_index])}")
        current_index += 1
    else:
        speak("No more songs in the queue.")

def pause_music():
    global paused
    if pygame.mixer.music.get_busy() and not paused:
        pygame.mixer.music.pause()
        paused = True
        speak("Music paused.")

def resume_music():
    global paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
        speak("Music resumed.")

def stop_music():
    global music_queue, current_index
    pygame.mixer.music.stop()
    music_queue = []
    current_index = 0
    speak("Music stopped.")

# Normalize input
text = input_text.lower().strip()

# Plugin command routing
if "add" in text and "to queue" in text:
    match = re.search(r"add (.+) to queue", text)
    if match:
        song = match.group(1).strip()
        result = add_to_queue(song)
        if result:
            speak(f"Added {result} to queue.")
        else:
            speak("Song not found.")
    else:
        speak("Please specify the song name to add.")

elif "play" in text and "music" in text:
    if music_queue:
        play_next()
    else:
        files = list_music()
        if files:
            music_queue.extend([os.path.join(MUSIC_DIR, f) for f in files])
            play_next()
        else:
            speak("No music files found.")

elif "pause" in text:
    pause_music()

elif "resume" in text:
    resume_music()

elif "stop" in text:
    stop_music()

elif "next" in text:
    play_next()

else:
    speak("Sorry, I couldn't catch that music command.")