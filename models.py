# models.py
import torch.nn as nn

INPUT_SIZE = 126   # لازم يطابق feature_extractor
HIDDEN_SIZE = 128

class Encoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(INPUT_SIZE, HIDDEN_SIZE, batch_first=True)

    def forward(self, x):
        _, (h, _) = self.lstm(x)
        return h[-1]


class Head(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.fc = nn.Linear(HIDDEN_SIZE, num_classes)

    def forward(self, x):
        return self.fc(x)
