import torch
from models import Encoder, Head
from feature_extractor import extract_keypoints

# ---------------- Config ----------------
DEVICE = "cpu"

LABELS = {
    0: "أهلاً"
}

NUM_CLASSES = len(LABELS)

# ---------------- Load Models ----------------
encoder = Encoder().to(DEVICE)
head = Head(num_classes=NUM_CLASSES).to(DEVICE)

try:
    encoder.load_state_dict(
        torch.load("model/base_model.pth", map_location=DEVICE)
    )
    head.load_state_dict(
        torch.load("model/incremental_head.pth", map_location=DEVICE)
    )
    print("✅ Models loaded successfully")
except Exception as e:
    print("❌ Failed to load models:", e)

encoder.eval()
head.eval()

# ---------------- Prediction ----------------
def predict(video_path):
    """
    Takes a video path and returns Arabic sentence
    """

    keypoints = extract_keypoints(video_path)
    if keypoints is None:
        return "مش قادر أفهم الإشارة"

    x = torch.tensor(
        keypoints,
        dtype=torch.float32
    ).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        features = encoder(x)
        logits = head(features)
        pred_id = torch.argmax(logits, dim=1).item()

    return LABELS.get(pred_id, "إشارة غير معروفة")
