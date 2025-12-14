'''🛠️ Requirements

Install the required packages:

pip install speechrecognition pyttsx3 pywhatkit wikipedia pyjokes'''

import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes

# Initialize the recognizer and voice engine
listener = sr.Recognizer()
engine = pyttsx3.init()

# Set voice (0 = male, 1 = female)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Change to 0 for male voice

def talk(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    try:
        with sr.Microphone() as source:
            print("🎙️ Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'alexa' in command:
                command = command.replace('alexa', '').strip()
                print(f"👉 Command: {command}")
    except Exception as e:
        print("Error:", e)
        return ""
    return command

def run_alexa():
    command = take_command()
    if 'play' in command:
        song = command.replace('play', '')
        talk(f"Playing {song}")
        pywhatkit.playonyt(song)

    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        talk(f"The current time is {time}")

    elif 'who is' in command:
        person = command.replace('who is', '')
        info = wikipedia.summary(person, 1)
        talk(info)

    elif 'joke' in command:
        talk(pyjokes.get_joke())

    elif 'stop' in command or 'exit' in command:
        talk("Goodbye!")
        exit()

    else:
        talk("Sorry, I didn’t understand. Please repeat.")

while True:
    run_alexa()
