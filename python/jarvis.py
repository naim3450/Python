# pip install speechrecognition sounddevice numpy pyautogui pygetwindow keyboard pyttsx3 requests gtts pyglet

import sounddevice as sd
import numpy as np
import speech_recognition as sr
import webbrowser
import pyautogui
import pygetwindow as gw
import keyboard
import time
import urllib.parse
import requests
import re
from gtts import gTTS
import pyglet
import os


# -------------------------------------------
# 🗣️ Speak
# -------------------------------------------
def speak(text):
    """Speak text using gTTS and pyglet"""
    print(f"🗣️ Speaking: {text}")
    tts = gTTS(text=text, lang='en')
    filename = "voice.mp3"
    tts.save(filename)

    music = pyglet.media.load(filename, streaming=False)
    music.play()

    # wait until audio finishes
    time.sleep(music.duration * 0.8)
    os.remove(filename)


# -------------------------------------------
# 🎤 Record Audio
# -------------------------------------------
def record_audio(duration=4, fs=44100):  # ⏱️ Reduced from 5 to 4 seconds
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
    print("📺 Opening YouTube...")
    speak("Opening YouTube")
    webbrowser.open("https://www.youtube.com/")
    time.sleep(2)  # ⏱️ Reduced from 5


def close_youtube():
    print("❌ Closing YouTube...")
    speak("Closing YouTube")
    for window in gw.getWindowsWithTitle('YouTube'):
        window.close()
        return
    keyboard.press_and_release('ctrl+w')


# -------------------------------------------
# 🔎 Search on YouTube
# -------------------------------------------
def search_youtube(query):
    print(f"🔍 Searching YouTube for: {query}")
    speak(f"Searching YouTube for {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    webbrowser.open(url)
    time.sleep(2)  # ⏱️ Reduced


# -------------------------------------------
# ▶️ Play first YouTube video
# -------------------------------------------
def play_youtube_video(query):
    print(f"🎬 Playing: {query}")
    speak(f"Playing {query} on YouTube")
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    try:
        response = requests.get(search_url).text
        match = re.search(r"watch\?v=(\S{11})", response)
        if match:
            video_id = match.group(1)
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            webbrowser.open(video_url)
            time.sleep(2)  # ⏱️ Reduced
        else:
            print("❌ Couldn't find a video for that search.")
            speak("I couldn't find that video")
    except Exception as e:
        print(f"⚠️ Error: {e}")
        speak("There was a problem connecting to YouTube")


# -------------------------------------------
# 🎧 Playlist Controls
# -------------------------------------------
MY_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLQHwpVpoHqSm5vHncQTVzBL9xrUGnKvCw"  # ✅ Direct playlist link

def open_playlist():
    print("🎵 Opening your playlist...")
    speak("Opening your YouTube playlist")
    webbrowser.open(MY_PLAYLIST_URL)
    time.sleep(2)


def play_playlist():
    print("🎶 Playing your playlist...")
    speak("Playing your playlist")
    webbrowser.open(MY_PLAYLIST_URL + "&playnext=1")
    time.sleep(2)


def next_video():
    print("⏭️ Going to next video...")
    speak("Playing next video")
    pyautogui.hotkey('shift', 'n')  # YouTube shortcut for next video


def previous_video():
    print("⏮️ Going to previous video...")
    speak("Playing previous video")
    pyautogui.hotkey('shift', 'p')  # Shortcut for previous video


# -------------------------------------------
# 🎛️ YouTube Playback Controls
# -------------------------------------------
def control_youtube(command):
    if "pause" in command or "play" in command:
        pyautogui.press('space')
    elif "forward" in command or "next" in command:
        pyautogui.press('l')
    elif "back" in command or "previous" in command:
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
    print("🤖 Jarvis ready! Try commands like:")
    print("   - 'open youtube'")
    print("   - 'close youtube'")
    print("   - 'search kesariya'")
    print("   - 'play kesariya'")
    print("   - 'open playlist'")
    print("   - 'play playlist'")
    print("   - 'next video', 'previous video'")
    print("   - 'pause', 'forward', 'mute'")
    print("   - 'exit' to quit\n")

    speak("Jarvis is ready. How can I help you?")

    while True:
        command = recognize_speech()
        if not command:
            continue

        if "open youtube" in command:
            open_youtube()

        elif "close youtube" in command:
            close_youtube()

        elif command.startswith("search "):
            query = command.replace("search", "").strip()
            search_youtube(query)

        elif command.startswith("play "):
            query = command.replace("play", "").strip()
            play_youtube_video(query)

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
            print("👋 Exiting Jarvis.")
            speak("Goodbye!")
            break


# -------------------------------------------
# 🏁 Run Jarvis
# -------------------------------------------
if __name__ == "__main__":
    jarvis()
