#MODEL_PATH='D:\\ITI\\9 Months Training AI\\NLP\\Final Project\\src\\emotion_classifier\\models\\lstm_emotion_classifier.pth'

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_PATH = "src/emotion_classifier/models/lstm_emotion_classifier.pth"