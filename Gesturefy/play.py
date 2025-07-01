import mediapipe as mp

def detect_thumbs_up(hand_landmarks):

    # Get landmark positions for the thumb and fingers
    thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_IP]
    index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]
    wrist = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]

    # Check if thumb is extended upwards (higher than index finger)
    thumb_up = thumb_tip.y < wrist.y and thumb_tip.y < thumb_ip.y

    # Check if other fingers are curled (tips lower than MCP joints)
    fingers_folded = (
        index_tip.y > hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP].y and
        middle_tip.y > hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP].y and
        ring_tip.y > hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP].y and
        pinky_tip.y > hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP].y
    )

    return thumb_up and fingers_folded
