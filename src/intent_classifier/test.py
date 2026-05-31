from classifier import IntentClassifier


classifier = IntentClassifier()

examples = [

    "hello",

    "thanks a lot",

    "goodbye",

    "I feel depressed and anxious",

    "I cannot stop worrying",

    "Who won the football match?",

    "What is the weather today?"
]

for text in examples:

    print("=" * 50)

    print("INPUT:")
    print(text)

    print()

    print("INTENT:")
    print(
        classifier.predict_with_metadata(text)
    )