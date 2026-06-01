from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

from ..llm_service.core.constants import STRONG_MODEL, WEAK_MODEL

# fix prompts import

from .prompts import (
    INTENT_PROMPT
)


class IntentClassifier:

    VALID_INTENTS = {
        "greeting",
        "goodbye",
        "gratitude",
        "asking_mental_health_question",
        "out_of_scope"
    }

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv('LLM_API_KEY')
        )

        self.model_name = STRONG_MODEL

    def predict(self, text: str, emotion: str) -> str:

        text = text.strip()
        if not text:
            return "out_of_scope"


        prompt = f"""
                    User message:
                    {text}

                    Detected emotion (from external model):
                    {emotion}

                    Now classify the user's intent.
                    """

        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0,
            max_completion_tokens=256,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an intent classifier.\n"
                        "You are given a user message and an emotion signal.\n\n"
                        "Return ONLY one of:\n"
                        "greeting\n"
                        "goodbye\n"
                        "gratitude\n"
                        "asking_mental_health_question\n"
                        "out_of_scope\n\n"
                        "IMPORTANT RULE:\n"
                        "- Do NOT output explanations\n"
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_response = (
            response.choices[0]
            .message
            .content
            .strip()
            .lower()
        )

        for intent in self.VALID_INTENTS:
            if intent in raw_response:
                return intent

        return "out_of_scope"
    
    
    def predict_with_metadata(self, text, emotion):
        intent = self.predict(text, emotion)
        return {"intent": intent}