from ..emotion_classifier.classifier.emotion_classifier_agent import EmotionAgent
agent = EmotionAgent()

examples = [
    "I feel anxious and can't sleep.",
    "I am sad all the time and need support.",
    "How can I calm down during a panic attack?",
    "I need help understanding my feelings.",
]

for text in examples:
    print("\nText:")
    print(text)
    print("Prediction:", agent.predict(text))
    print('#'*50)