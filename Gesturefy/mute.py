import mediapipe as mp
import numpy as np

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

def detect_pinch(hand_landmarks):
    # Get the coordinates of the thumb tip and index finger tip
    thumb_tip = np.array([hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x,
                          hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y])
    index_tip = np.array([hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x,
                          hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y])
    
    # Calculate the distance between thumb tip and index finger tip
    distance = np.linalg.norm(thumb_tip - index_tip)
    
    # Define a threshold distance for pinch gesture
    threshold = 0.05
    
    # Check if the distance is less than the threshold
    return distance < threshold