import torch
import os

from .lstm_classifier import LSTMClassifier   # you must have model class

from ..core.constants import MODEL_PATH, DEVICE

class EmotionAgent:

    def __init__(self, model_path=MODEL_PATH):

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")

        checkpoint = torch.load(model_path, map_location=DEVICE, weights_only=True)

        self.model = LSTMClassifier(
            vocab_size=checkpoint["config"]["vocab_size"],
            embed_dim=checkpoint["config"]["embed_dim"],
            hidden_dim=checkpoint["config"]["hidden_dim"],
            num_layers=checkpoint["config"]["num_layers"],
            num_classes=checkpoint["config"]["num_classes"],
            pad_idx=checkpoint["config"]["pad_idx"]
        )
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(DEVICE)
        self.model.eval()

        self.vocab = checkpoint["vocab"]

        self.pad_idx = self.vocab["<PAD>"]
        self.unk_idx = self.vocab["<UNK>"]

    def preprocess(self, text):
        return text.lower().strip()

    def tokenize(self, text):
        return text.split()

    def encode(self, text, max_len=64):

        tokens = self.tokenize(text)

        ids = [
            self.vocab.get(t, self.unk_idx)
            for t in tokens
        ]

        ids = ids[:max_len]

        if len(ids) < max_len:
            ids += [self.pad_idx] * (max_len - len(ids))

        return torch.tensor(ids, dtype=torch.long).unsqueeze(0).to(DEVICE)

    def predict(self, text):

        x = self.encode(self.preprocess(text))

        with torch.no_grad():
            logits = self.model(x)
            pred = logits.argmax(dim=1).item()
        mapping = {
        0: "sadness",
        1: "joy",
        2: "love",
        3: "anger",
        4: "fear",
        5: "surprise"
}

        return mapping.get(pred, "unknown")