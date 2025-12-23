import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands

def extract_keypoints(video_path, max_frames=30):
    cap = cv2.VideoCapture(video_path)
    seq = []

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:

        while cap.isOpened() and len(seq) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame)

            frame_kp = np.zeros(126)  # 2 hands * 21 landmarks * 3

            if results.multi_hand_landmarks:
                for h_idx, hand in enumerate(results.multi_hand_landmarks):
                    if h_idx >= 2:
                        break
                    for i, lm in enumerate(hand.landmark):
                        base = h_idx * 63
                        frame_kp[base + i*3 : base + i*3 + 3] = [lm.x, lm.y, lm.z]

            seq.append(frame_kp)

    cap.release()

    while len(seq) < max_frames:
        seq.append(np.zeros(126))

    return np.array(seq)
