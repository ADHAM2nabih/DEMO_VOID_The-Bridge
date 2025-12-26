import cv2
import mediapipe as mp
import numpy as np
import os

mp_hands = mp.solutions.hands

def extract_keypoints(video_path, target_frames=45):
    if not os.path.exists(video_path):
        return None

    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    if len(frames) == 0:
        return None

    indices = np.linspace(0, len(frames)-1, target_frames, dtype=int)
    selected_frames = [frames[i] for i in indices]

    sequence = []

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as hands:

        for frame in selected_frames:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            frame_kp = np.zeros(126, dtype=np.float32)

            if results.multi_hand_landmarks and results.multi_handedness:
                hands_data = []

                for lm, handed in zip(results.multi_hand_landmarks,
                                       results.multi_handedness):
                    label = handed.classification[0].label  # Right / Left
                    hands_data.append((label, lm))

                # ترتيب ثابت: Right ثم Left
                hands_data.sort(key=lambda x: x[0], reverse=True)

                for h_idx, (_, hand) in enumerate(hands_data[:2]):
                    wrist = hand.landmark[0]
                    middle = hand.landmark[9]

                    scale = np.linalg.norm([
                        middle.x - wrist.x,
                        middle.y - wrist.y,
                        middle.z - wrist.z
                    ])
                    scale = scale if scale > 0 else 1.0

                    base = h_idx * 63
                    for i, lm in enumerate(hand.landmark):
                        frame_kp[base + i*3]     = (lm.x - wrist.x) / scale
                        frame_kp[base + i*3 + 1] = (lm.y - wrist.y) / scale
                        frame_kp[base + i*3 + 2] = (lm.z - wrist.z) / scale

            sequence.append(frame_kp)

    return np.array(sequence)
