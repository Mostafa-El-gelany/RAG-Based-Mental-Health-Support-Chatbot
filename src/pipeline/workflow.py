from .chat_engine import ChatEngine


def run():
    engine = ChatEngine()
    while True:
        user_prompt = input("Enter your message\n")
        result = engine.process_message(user_prompt)
        print(f"Detected Language: {result['detected_language']}\n")
        print(f"Detected Emotion: {result['emotion']}\n")
        print(f"Identified Intent: {result['intent']}\n")
        print(f"Translated Prompt: {result['translated_prompt']}\n")

        if result["intent"] == "asking_mental_health_question":
            print(f"Rewritten Query: {result['rewritten_query']}\n")
            for idx, item in enumerate(result["results"], start=1):
                print(f"Result {idx}:")
                print(f"Context: {item.payload['context']}")
                print(f"Response: {item.payload['response']}")
                print(f"Chunk: {item.payload['chunk']}\n")

        print(f"🤖 LLM Response: {result['assistant_response']}")
