import cv2
import mediapipe as mp
import numpy as np
import threading
import time
from mute import detect_pinch
from volume import measure_distance
from play import detect_thumbs_up
from tracks import detect_swipe
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import creds

# === Spotify Setup ===
client_id = creds.client_id
client_secret = creds.client_secret
redirect_uri = creds.redirect_uri
scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)
token_info = sp_oauth.get_cached_token()

if not token_info:
    token_info = sp_oauth.get_access_token()

access_token = token_info['access_token'] if isinstance(token_info, dict) else token_info
sp = spotipy.Spotify(auth=access_token)

# === Mediapipe Setup ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.96)
mp_drawing = mp.solutions.drawing_utils

# === OpenCV Setup ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# === Volume Control Constants ===
MIN_DISTANCE = 0.02
MAX_DISTANCE = 0.6
prev_volume = None

# === Swipe Gesture State ===
swipe_candidate = None
swipe_start_time = None
SWIPE_HOLD_TIME = 0.5  # seconds
SWIPE_COOLDOWN = 1.0  # seconds
last_swipe_time = 0

# === Track Change Lock ===
track_change_locked = False

# === Frame Thread ===
class VideoCaptureThread(threading.Thread):
    def __init__(self, cap):
        super().__init__()
        self.cap = cap
        self.frame = None

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

# Start capture thread
capture_thread = VideoCaptureThread(cap)
capture_thread.start()

# === Main Loop ===
frame_count = 0
while True:
    if capture_thread.frame is not None:
        frame = capture_thread.frame
        frame_count += 1

        if frame_count % 2 == 0:  # Reduce processing load
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            current_time = time.time()

            # Volume control lock check
            track_change_locked = len(results.multi_hand_landmarks or []) == 2

            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    hand_label = handedness.classification[0].label.lower()

                    # Swipe gestures (only if track change is unlocked)
                    if not track_change_locked:
                        swipe_result = detect_swipe(hand_landmarks)

                        if swipe_result in ['left', 'right']:
                            if swipe_candidate is None:
                                swipe_candidate = swipe_result
                                swipe_start_time = current_time
                            elif swipe_result == swipe_candidate and (current_time - swipe_start_time) >= SWIPE_HOLD_TIME:
                                if current_time - last_swipe_time > SWIPE_COOLDOWN:
                                    try:
                                        if swipe_result == 'left':
                                            sp.previous_track()
                                            print("Swiped Left → Previous Track")
                                        else:
                                            sp.next_track()
                                            print("Swiped Right → Next Track")
                                        last_swipe_time = current_time
                                    except Exception as e:
                                        print(f"Error switching track: {e}")
                                    swipe_candidate = None
                                    swipe_start_time = None
                        else:
                            swipe_candidate = None
                            swipe_start_time = None

                    # Detect pinch → pause
                    if detect_pinch(hand_landmarks):
                        cv2.putText(frame, 'Pinch Detected! Pausing...', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        try:
                            sp.pause_playback()
                        except Exception as e:
                            print(f"Error pausing: {e}")

                    # Detect thumbs-up → play
                    if detect_thumbs_up(hand_landmarks):
                        cv2.putText(frame, 'Thumbs Up! Resuming...', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        try:
                            sp.start_playback()
                        except Exception as e:
                            print(f"Error resuming: {e}")

                # Volume Control: Two hands → control volume
                if len(results.multi_hand_landmarks) == 2:
                    hand1, hand2 = results.multi_hand_landmarks
                    distance = measure_distance(hand1, hand2)
                    cv2.putText(frame, f'Distance: {distance:.2f}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                    volume = int(np.interp(distance, [MIN_DISTANCE, MAX_DISTANCE], [0, 100]))
                    volume = max(0, min(100, volume))

                    if prev_volume is None or abs(prev_volume - volume) > 5:
                        try:
                            sp.volume(volume)
                            print(f"Volume set to {volume}")
                            prev_volume = volume
                        except Exception as e:
                            print(f"Error setting volume: {e}")

            # Show frame
            cv2.imshow("Gesture Control", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# Cleanup
cap.release()
cv2.destroyAllWindows()
