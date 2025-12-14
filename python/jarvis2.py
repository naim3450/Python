# pip install speechrecognition sounddevice numpy pyautogui pygetwindow keyboard requests pyttsx3

import sounddevice as sd
import numpy as np
import speech_recognition as sr
import webbrowser
import pyautogui
import pygetwindow as gw
import keyboardm
import time
import urllib.parse
import requests
import re
import threading
import pyttsx3


# -------------------------------------------
# 🗣️ Instant Speak (offline)
# -------------------------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 1.0)

def speak(text):
    print(f"🗣️ Speaking: {text}")
    threading.Thread(target=lambda: engine.say(text) or engine.runAndWait()).start()


# -------------------------------------------
# 🎤 Record Audio
# -------------------------------------------
def record_audio(duration=3, fs=44100):
    print("🎤 Listening...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()
    return np.squeeze(audio_data)


# -------------------------------------------
# 🧠 Recognize Speech
# -------------------------------------------
def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        audio = record_audio()
        audio_data = sr.AudioData(audio.tobytes(), 44100, 2)
        text = recognizer.recognize_google(audio_data)
        print(f"🗣️ You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("❌ Sorry, I couldn't understand that.")
        return ""
    except sr.RequestError:
        print("⚠️ Speech recognition service unavailable.")
        return ""


# -------------------------------------------
# 📺 YouTube Controls
# -------------------------------------------
def open_youtube():
    speak("Opening YouTube")
    webbrowser.open("https://www.youtube.com/")


def close_youtube():
    speak("Closing YouTube")
    for window in gw.getWindowsWithTitle('YouTube'):
        window.close()
        return
    keyboard.press_and_release('ctrl+w')


def search_youtube(query):
    speak(f"Searching YouTube for {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    webbrowser.open(url)


def play_youtube_video(query):
    speak(f"Playing {query} on YouTube")
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    try:
        response = requests.get(search_url).text
        match = re.search(r"watch\?v=(\S{11})", response)
        if match:
            video_id = match.group(1)
            webbrowser.open(f"https://www.youtube.com/watch?v={video_id}")
        else:
            speak("I couldn't find that video")
    except Exception:
        speak("There was a problem connecting to YouTube")


# -------------------------------------------
# 🎧 Playlist Controls
# -------------------------------------------
MY_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLQHwpVpoHqSm5vHncQTVzBL9xrUGnKvCw"

def open_playlist():
    speak("Opening your YouTube playlist")
    webbrowser.open(MY_PLAYLIST_URL)

def play_playlist():
    speak("Playing your playlist")
    webbrowser.open(MY_PLAYLIST_URL + "&playnext=1")

def next_video():
    speak("Next video")
    pyautogui.hotkey('shift', 'n')

def previous_video():
    speak("Previous video")
    pyautogui.hotkey('shift', 'p')


# -------------------------------------------
# 🎛️ YouTube Controls
# -------------------------------------------
def control_youtube(command):
    if "pause" in command or "play" in command:
        pyautogui.press('space')
    elif "forward" in command:
        pyautogui.press('l')
    elif "back" in command:
        pyautogui.press('j')
    elif "mute" in command:
        pyautogui.press('m')
    elif "full screen" in command:
        pyautogui.press('f')
    elif "exit full" in command:
        pyautogui.press('esc')
    elif "next video" in command:
        next_video()
    elif "previous video" in command:
        previous_video()


# -------------------------------------------
# 🤖 Main Jarvis Loop
# -------------------------------------------
def jarvis():
    speak("Jarvis is online. Ready for your command.")
    print("\n⚡ Fast Jarvis is ready!\n")

    while True:
        command = recognize_speech()
        if not command:
            continue

        if "open youtube" in command:
            open_youtube()
        elif "close youtube" in command:
            close_youtube()
        elif command.startswith("search "):
            search_youtube(command.replace("search", "").strip())
        elif command.startswith("play "):
            play_youtube_video(command.replace("play", "").strip())
        elif "open playlist" in command:
            open_playlist()
        elif "play playlist" in command:
            play_playlist()
        elif "next video" in command:
            next_video()
        elif "previous video" in command:
            previous_video()
        elif any(word in command for word in ["pause", "forward", "back", "mute", "full screen", "exit full"]):
            control_youtube(command)
        elif "exit" in command or "quit" in command:
            speak("Goodbye!")
            break


if __name__ == "__main__":
    jarvis()
