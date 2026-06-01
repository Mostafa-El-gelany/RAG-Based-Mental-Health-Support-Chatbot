import torch
import torch.nn as nn

# 1. define model (MUST match training)
class LSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers, num_classes, pad_idx):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)

        self.lstm = nn.LSTM(
            embed_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True
        )

        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        _, (h, _) = self.lstm(x)
        h = torch.cat((h[-2], h[-1]), dim=1)
        return self.fc(h)


# 2. load checkpoint
checkpoint = torch.load(
    "src/emotion_classifier/models/lstm_emotion_classifier.pth",
    map_location="cpu"
)

vocab = checkpoint["vocab"]
config = checkpoint["config"]

pad_idx = vocab["<PAD>"]

# 3. rebuild model
model = LSTMClassifier(
    vocab_size=config["vocab_size"],
    embed_dim=config["embed_dim"],
    hidden_dim=config["hidden_dim"],
    num_layers=config["num_layers"],
    num_classes=config["num_classes"],
    pad_idx=pad_idx
)

# 4. load weights
model.load_state_dict(checkpoint["model_state_dict"])

# 5. eval mode
model.eval()

print("Model loaded successfully")