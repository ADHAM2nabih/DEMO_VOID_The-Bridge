import os
import torch
import torch.nn as nn
import random
from torch.utils.data import DataLoader
from models import Encoder, Head
from feature_extractor import extract_keypoints

DEVICE = "cpu"
DATA_DIR = "data"
MODEL_DIR = "model"
os.makedirs(MODEL_DIR, exist_ok=True)

BASE_MODEL_PATH = os.path.join(MODEL_DIR, "base_model.pth")
HEAD_MODEL_PATH = os.path.join(MODEL_DIR, "head_model.pth")

EPOCHS = 150
LR = 1e-4
BATCH_SIZE = 8

LABELS = {
    "hello": 0, "all good": 1, "drink": 2, "help": 3, "hospital": 4,
    "hungry": 5, "love": 6, "not good": 7, "quran": 8, "sleep": 9,
    "what is your name": 10
}

def temporal_jitter(x, max_shift=3):
    shift = random.randint(-max_shift, max_shift)
    return torch.roll(x, shifts=shift, dims=0)

def build_dataset():
    data = []

    for label, idx in LABELS.items():
        folder = os.path.join(DATA_DIR, label)
        if not os.path.isdir(folder):
            continue

        for video in os.listdir(folder):
            kp = extract_keypoints(os.path.join(folder, video))
            if kp is None:
                continue

            base = torch.tensor(kp, dtype=torch.float32)
            y = torch.tensor(idx)

            data.append((base, y))

            # Augmentation محدود + ذكي
            for _ in range(8):
                aug = temporal_jitter(base)
                data.append((aug, y))

    return data

def train():
    dataset = build_dataset()
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    encoder = Encoder().to(DEVICE)
    head = Head(num_classes=len(LABELS)).to(DEVICE)

    # قفل encoder في الأول
    for p in encoder.parameters():
        p.requires_grad = False

    optimizer = torch.optim.Adam(head.parameters(), lr=LR)
    loss_fn = nn.CrossEntropyLoss()

    print(f"Training on {len(dataset)} samples")

    for epoch in range(EPOCHS):
        encoder.train()
        head.train()
        total_loss = 0

        # فتح encoder بعد 60 epoch
        if epoch == 60:
            for p in encoder.parameters():
                p.requires_grad = True
            optimizer = torch.optim.Adam(
                list(encoder.parameters()) + list(head.parameters()), lr=LR/2
            )

        for X, y in loader:
            X = X.to(DEVICE)
            y = y.to(DEVICE)

            optimizer.zero_grad()
            out = head(encoder(X))
            loss = loss_fn(out, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss:.4f}")

    torch.save(encoder.state_dict(), BASE_MODEL_PATH)
    torch.save(head.state_dict(), HEAD_MODEL_PATH)
    print("✅ Training Finished & Saved")

if __name__ == "__main__":
    train()
