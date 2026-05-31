import joblib
import os


class LanguageDetector:

    def __init__(self, model_path: str = None):
        # Default model path is relative to the package `Language_Detection` directory
        if model_path is None:
            package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            model_path = os.path.join(package_root, "models", "language_detector.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Language detection model not found at: {model_path}")

        self.model = joblib.load(model_path)
    def preprocess(self, text):
        return " ".join(text.split())
    
    def predict(self, text):
        text = self.preprocess(text)
        return self.model.predict([text])[0]
    
    def predict_proba(self, text):
        text = self.preprocess(text)
        probs = self.model.predict_proba([text])[0]
        classes = self.model.classes_
        return dict(zip(classes, probs))

    def predict_top_k(self,text,k=3):
        probs = self.predict_proba(text)
        return sorted(probs.items(), key=lambda x: x[1], reverse=True)[:k]