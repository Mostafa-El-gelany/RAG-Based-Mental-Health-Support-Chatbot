from src.Language_Detection.detector import LanguageDetector
detector = LanguageDetector()

examples = [
    "Hello welcom",
    "مرحبا كيف حالك",
    "Bonjour tout le monde",
    "Hola amigo",
    "Привет как дела",
    'hi',
    'hello'
]

for text in examples:
    print("\nText:")
    print(text)
    print("Prediction:", detector.predict(text))
    print("Top 3:",detector.predict_top_k(text))
    print('#'*50)