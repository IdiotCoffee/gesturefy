import mediapipe as mp

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def detect_swipe(hand_landmarks):
    """
    Detect swipe gestures by checking hand position changes
    Returns: 'left' for left swipe, 'right' for right swipe, None for no swipe.
    """
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    if wrist.x - index_tip.x > 0.1:
        return 'left'
    elif index_tip.x - wrist.x > 0.1:
        return 'right'
    return None
