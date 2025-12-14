"""
people_counter.py

Requirements:
  pip install opencv-python pyttsx3 numpy

How it works (summary):
  - Uses OpenCV Haar cascade to detect faces.
  - Uses OpenCV HOG+SVM people detector for full-body detections.
  - Merges overlapping detections (simple IoU-based merging).
  - Chooses a conservative count (max of unique faces and unique merged person boxes).
  - Announces count with pyttsx3 TTS and shows bounding boxes on video.

Run:
  python people_counter.py
Press 'q' to quit.
"""

import cv2
import numpy as np
import pyttsx3
import time

# --- Utilities ---
def iou(boxA, boxB):
    # box = (x, y, w, h)
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0]+boxA[2], boxB[0]+boxB[2])
    yB = min(boxA[1]+boxA[3], boxB[1]+boxB[3])
    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH
    boxAArea = boxA[2]*boxA[3]
    boxBArea = boxB[2]*boxB[3]
    union = boxAArea + boxBArea - interArea
    return interArea / union if union > 0 else 0

def merge_boxes(boxes, iou_thresh=0.3):
    """
    Merge boxes if IoU > threshold (simple greedy clustering).
    """
    boxes = boxes.copy()
    merged = []
    while boxes:
        base = boxes.pop(0)
        bx, by, bw, bh = base
        to_merge = []
        i = 0
        while i < len(boxes):
            if iou(base, boxes[i]) > iou_thresh:
                to_merge.append(boxes.pop(i))
            else:
                i += 1
        # combine base and to_merge into a single bounding box (bounding union)
        xs = [bx, bx + bw]
        ys = [by, by + bh]
        for m in to_merge:
            xs.append(m[0]); xs.append(m[0]+m[2])
            ys.append(m[1]); ys.append(m[1]+m[3])
        x1, x2 = min(xs), max(xs)
        y1, y2 = min(ys), max(ys)
        merged.append((x1, y1, x2-x1, y2-y1))
    return merged

# --- Setup detectors ---
# Haar cascade for face detection (comes with OpenCV)
face_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(face_cascade_path)

# HOG person detector (works best for standing / upright people)
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Setup TTS
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # speak rate
last_announced_count = None
last_announce_time = 0
announce_interval = 5.0  # seconds between announcements minimum

# Video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Could not open webcam. Check device index or drivers.")
    exit(1)

print("Starting webcam. Press 'q' to quit.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("WARNING: failed to read frame from webcam")
            break

        # Resize to speed up (adjust as needed)
        scale = 640.0 / frame.shape[1]
        frame_small = cv2.resize(frame, (640, int(frame.shape[0]*scale)))

        gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)

        # 1) Face detection
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))
        faces_list = [(int(x), int(y), int(w), int(h)) for (x,y,w,h) in faces]

        # 2) HOG person detection
        # returns rects (x, y, w, h)
        rects, weights = hog.detectMultiScale(frame_small,
                                              winStride=(8,8),
                                              padding=(8,8),
                                              scale=1.05)
        persons = [(int(x), int(y), int(w), int(h)) for (x,y,w,h) in rects]

        # Merge person boxes to avoid double-counting
        merged_persons = merge_boxes(persons, iou_thresh=0.4)

        # Heuristic: the estimated count is max(number of unique faces, number of merged person boxes)
        # (Faces are more precise for seated/talking people; HOG helps detect whole bodies)
        est_count = max(len(faces_list), len(merged_persons))

        # Draw faces (blue) and person boxes (green) on frame_small
        for (x,y,w,h) in merged_persons:
            cv2.rectangle(frame_small, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame_small, "Person", (x, y-6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        for (x,y,w,h) in faces_list:
            cv2.rectangle(frame_small, (x,y), (x+w,y+h), (255,0,0), 2)
            cv2.putText(frame_small, "Face", (x, y-6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,0,0), 1)

        # Show count on frame
        text = f"Estimated people: {est_count}"
        cv2.putText(frame_small, text, (10, frame_small.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

        cv2.imshow("People counter", frame_small)

        # Announce if count changed or if long time passed
        now = time.time()
        should_announce = False
        if last_announced_count != est_count and (now - last_announce_time) > 1.0:
            should_announce = True
        elif (now - last_announce_time) > announce_interval:
            should_announce = True

        if should_announce:
            try:
                # Compose phrase
                if est_count == 0:
                    phrase = "No people detected in the room."
                elif est_count == 1:
                    phrase = "One person is present in the room."
                else:
                    phrase = f"{est_count} people are present in the room."
                # Announce (non-blocking)
                tts_engine.say(phrase)
                tts_engine.runAndWait()
            except Exception as e:
                # if TTS fails, just print
                print("TTS error:", e)
                print("Count:", est_count)

            last_announced_count = est_count
            last_announce_time = now

        # Key handling
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    try:
        tts_engine.stop()
    except Exception:
        pass
