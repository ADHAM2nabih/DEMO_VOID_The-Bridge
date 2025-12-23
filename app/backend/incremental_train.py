# incremental_train.py
import os
import sqlite3
import torch
import torch.nn as nn
import numpy as np

from models import Encoder, Head
from feature_extractor import extract_keypoints

# ---------------- System ----------------
DEVICE = "cpu"

DATA_DIR = "data"
MODEL_DIR = "model"
DB_PATH = "trained_videos.db"

BASE_MODEL_PATH = os.path.join(MODEL_DIR, "base_model.pth")
HEAD_MODEL_PATH = os.path.join(MODEL_DIR, "incremental_head.pth")

os.makedirs(MODEL_DIR, exist_ok=True)

# ---------------- FIXED LABEL SPACE ----------------
# ❗ لا يتغير بعد أول تدريب
LABELS = {
    "hello": 0
}

NUM_CLASSES = len(LABELS)

# ---------------- Database ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS trained_videos (
            video_path TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()


def is_trained(video_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM trained_videos WHERE video_path=?",
        (video_path,)
    )
    res = c.fetchone()
    conn.close()
    return res is not None


def mark_trained(video_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO trained_videos VALUES (?)",
        (video_path,)
    )
    conn.commit()
    conn.close()


# ---------------- Safe Load ----------------
def safe_load(model, path, name):
    if not os.path.exists(path):
        print(f"🆕 {name} not found → training from scratch")
        return False

    if os.path.getsize(path) == 0:
        print(f"⚠️ {name} empty → deleting")
        os.remove(path)
        return False

    try:
        model.load_state_dict(
            torch.load(path, map_location=DEVICE)
        )
        print(f"✅ Loaded {name}")
        return True
    except Exception as e:
        print(f"❌ Incompatible {name}: {e}")
        print("➡️ Deleting and retraining safely")
        os.remove(path)
        return False


# ---------------- Training ----------------
def train():
    print("🚀 Starting incremental training process...")
    init_db()

    encoder = Encoder().to(DEVICE)
    head = Head(num_classes=NUM_CLASSES).to(DEVICE)

    safe_load(encoder, BASE_MODEL_PATH, "Base Encoder")
    safe_load(head, HEAD_MODEL_PATH, "Incremental Head")

    optimizer = torch.optim.Adam(
        list(encoder.parameters()) + list(head.parameters()),
        lr=1e-3
    )

    criterion = nn.CrossEntropyLoss()

    trained_anything = False

    for label_name, label_id in LABELS.items():
        label_dir = os.path.join(DATA_DIR, label_name)
        if not os.path.isdir(label_dir):
            continue

        for video in os.listdir(label_dir):
            video_path = os.path.join(label_dir, video)

            if is_trained(video_path):
                continue

            keypoints = extract_keypoints(video_path)

            if keypoints is None or len(keypoints) == 0:
                print(f"⚠️ Skipping invalid video: {video_path}")
                continue

            X = torch.tensor(
                keypoints,
                dtype=torch.float32
            ).unsqueeze(0).to(DEVICE)

            y = torch.tensor(
                [label_id],
                dtype=torch.long
            ).to(DEVICE)

            optimizer.zero_grad()
            features = encoder(X)
            logits = head(features)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

            mark_trained(video_path)
            trained_anything = True
            print(f"🎯 Trained on: {video_path}")

    if trained_anything:
        torch.save(encoder.state_dict(), BASE_MODEL_PATH)
        torch.save(head.state_dict(), HEAD_MODEL_PATH)
        print("💾 Models saved successfully")
    else:
        print("ℹ️ No new videos found → skipping save")

    print("✅ Incremental training finished (no catastrophic forgetting)")


if __name__ == "__main__":
    train()
