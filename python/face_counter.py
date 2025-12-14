"""
face_counter_talker.py
Detect faces from webcam, show the count on-screen and speak the number
whenever it changes.

Dependencies:
    pip install opencv-python pyttsx3

Notes:
- On Linux you may need `espeak` or other TTS backend installed for pyttsx3.
- Press 'q' to quit the program.
"""

import time
import cv2
import pyttsx3

def speak_text(engine, text):
    """Speak text using pyttsx3 in a non-blocking way (uses runAndWait)."""
    engine.say(text)
    engine.runAndWait()

def main():
    # Initialize TTS engine
    engine = pyttsx3.init()
    # Optional: tweak voice rate/volume
    rate = engine.getProperty('rate')
    engine.setProperty('rate', max(120, rate - 20))  # a bit slower
    volume = engine.getProperty('volume')
    engine.setProperty('volume', volume)  # 0.0 to 1.0

    # Initialize face detector (Haar cascade included with opencv)
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        raise RuntimeError("Failed to load Haar cascade. Check OpenCV installation.")

    # Open default webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    prev_count = -1
    last_spoken_time = 0.0
    # Minimum seconds between speaking events to avoid rapid repetition
    MIN_SPEAK_GAP = 0.8

    print("Starting webcam. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed reading frame from webcam — exiting.")
            break

        # Optional: resize to speed up detection (adjust as needed)
        small = cv2.resize(frame, (0, 0), fx=0.6, fy=0.6)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        # Detect faces. tweak scaleFactor and minNeighbors for your environment
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Draw rectangles around faces (scale coordinates back to full frame)
        scale_x = frame.shape[1] / small.shape[1]
        scale_y = frame.shape[0] / small.shape[0]
        for (x, y, w, h) in faces:
            x1 = int(x * scale_x)
            y1 = int(y * scale_y)
            x2 = int((x + w) * scale_x)
            y2 = int((y + h) * scale_y)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        count = len(faces)

        # If the count changed, speak it (with a small debounce)
        now = time.time()
        if count != prev_count and (now - last_spoken_time) >= MIN_SPEAK_GAP:
            # Human-friendly phrasing
            if count == 0:
                phrase = "No people in the room."
            elif count == 1:
                phrase = "One person."
            else:
                phrase = f"{count} people."
            # Speak (blocking until finished). If you prefer non-blocking,
            # run speak_text in a separate thread.
            try:
                speak_text(engine, phrase)
                last_spoken_time = now
            except Exception as e:
                print("TTS error:", e)

            prev_count = count

        # Overlay the count on the video
        label = f"Faces: {count}"
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow('Face Counter', frame)

        # Quit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    # Clean up TTS engine
    try:
        engine.stop()
    except Exception:
        pass

if __name__ == "__main__":
    main()
