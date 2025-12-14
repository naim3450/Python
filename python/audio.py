from pydub import AudioSegment

# Load the uploaded audio file
audio_path = "Premika_Ne_Pyaar_Se.mp3"
audio = AudioSegment.from_file(audio_path)

# Get duration in seconds
duration_seconds = len(audio) / 1000
duration_seconds
print(duration_seconds)
