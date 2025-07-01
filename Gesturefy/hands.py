import cv2
import mediapipe as mp
import numpy as np
import threading
from mute import detect_pinch
from volume import measure_distance
from play import detect_thumbs_up
from tracks import detect_swipe
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import creds

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.96)
mp_drawing = mp.solutions.drawing_utils

# Initialize OpenCV (set resolution to 640x480)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize Spotify API
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

# Variables
prev_volume = None
MIN_DISTANCE = 0.02  # Min distance for volume
MAX_DISTANCE = 0.6  # Max distance for volume
frame_count = 0

# Threaded video capture
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

# Start the capture thread
capture_thread = VideoCaptureThread(cap)
capture_thread.start()

while True:
    if capture_thread.frame is not None:
        frame = capture_thread.frame
        frame_count += 1

        # Skip frames to reduce load
        if frame_count % 2 == 0:  # Process every 2nd frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame and get hand landmarks
            results = hands.process(frame_rgb)

            # Draw hand landmarks and check gestures
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    hand_label = "left" if handedness.classification[0].label.lower() == "left" else "right"

                    # In your main loop where hands are being processed:
                    if detect_swipe(hand_landmarks) == 'left':
                        try:
                            sp.previous_track()  # Move to previous track
                        except Exception as e:
                            print(f"Error switching to previous track: {e}")

                    if detect_swipe(hand_landmarks) == 'right':
                        try:
                            sp.next_track()  # Move to next track
                        except Exception as e:
                            print(f"Error switching to next track: {e}")

                    # Detect pinch gesture for pausing music
                    if detect_pinch(hand_landmarks):
                        cv2.putText(frame, 'Pinch Detected! Pausing...', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                        try:
                            sp.pause_playback()  # Pause Spotify playback
                        except Exception as e:
                            print(f"Error pausing playback: {e}")

                    # Detect thumbs-up gesture to resume music
                    if detect_thumbs_up(hand_landmarks):
                        cv2.putText(frame, 'Thumbs Up! Resuming...', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
                        try:
                            sp.start_playback()  # Resume Spotify playback
                        except Exception as e:
                            print(f"Error resuming playback: {e}")

                # Check if two hands are detected for volume control
                if len(results.multi_hand_landmarks) == 2:
                    hand1, hand2 = results.multi_hand_landmarks

                    # Measure the distance between index fingers
                    distance = measure_distance(hand1, hand2)
                    cv2.putText(frame, f'Distance: {distance:.2f}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                    # Map the distance to volume (0-100)
                    volume = int(np.interp(distance, [MIN_DISTANCE, MAX_DISTANCE], [0, 100]))
                    volume = max(0, min(100, volume))  # Ensure it's within range

                    # Set volume only if changed significantly
                    if prev_volume is None or abs(prev_volume - volume) > 5:
                        try:
                            sp.volume(volume)
                            prev_volume = volume
                            print(f"Setting volume to {volume}")
                        except Exception as e:
                            print(f"Error setting volume: {e}")

            # Display the frame
            cv2.imshow('Hand Gesture Recognition', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# Release resources
cap.release()
cv2.destroyAllWindows()
