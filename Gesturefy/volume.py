import math
import mediapipe as mp

def measure_distance(hand_landmarks_left, hand_landmarks_right):
    index_left = hand_landmarks_left.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
    index_right = hand_landmarks_right.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]

    # Calculate Euclidean distance (normalized)
    distance = math.sqrt((index_right.x - index_left.x) ** 2 + (index_right.y - index_left.y) ** 2)

    return distance
