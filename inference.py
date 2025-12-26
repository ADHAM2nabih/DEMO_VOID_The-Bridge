import torch
import os
from models import Encoder, Head
from feature_extractor import extract_keypoints

DEVICE = "cpu"
MODEL_DIR = "model"

LABELS = {
    "hello": 0, "all good": 1, "drink": 2, "help": 3, "hospital": 4,
    "hungry": 5, "love": 6, "not good": 7, "quran": 8, "sleep": 9,
    "what is your name": 10
}

TRANSLATIONS = {
    "hello": "أهلاً",
    "all good": "كله تمام",
    "drink": "عايز أشرب",
    "help": "ساعدني",
    "hospital": "محتاج مستشفى",
    "hungry": "جعان",
    "love": "بحبك",
    "not good": "مش كويس",
    "quran": "بحفظ قرآن",
    "sleep": "عايز أنام",
    "what is your name": "اسمك ايه؟"
}

CONFIDENCE_THRESHOLD = 0.75

encoder = Encoder().to(DEVICE)
head = Head(num_classes=len(LABELS)).to(DEVICE)

encoder.load_state_dict(torch.load(os.path.join(MODEL_DIR, "base_model.pth"), map_location=DEVICE))
head.load_state_dict(torch.load(os.path.join(MODEL_DIR, "head_model.pth"), map_location=DEVICE))

encoder.eval()
head.eval()

def predict(video_path):
    kp = extract_keypoints(video_path)
    if kp is None:
        return "مش واضح"

    X = torch.tensor(kp, dtype=torch.float32).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = head(encoder(X))
        probs = torch.softmax(logits, dim=1)
        conf, idx = torch.max(probs, dim=1)

    if conf.item() < CONFIDENCE_THRESHOLD:
        return "غير متأكد – حاول تاني"

    label = list(LABELS.keys())[idx.item()]
    return TRANSLATIONS[label]
