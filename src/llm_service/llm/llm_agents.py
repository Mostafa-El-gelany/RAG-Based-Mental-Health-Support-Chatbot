from groq import Groq
from ..core.constants import WEAK_MODEL, STRONG_MODEL
import os
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("LLM_API_KEY")
        )

        self.model = WEAK_MODEL

        self.messages = [
            {
                "role": "system",
                "content": """
                You are a supportive mental health assistant.

                You may be provided with retrieved counseling examples from a knowledge base.
                Use them as reference material but do not copy them verbatim.

                Always prioritize:
                1. Empathy
                2. Safety
                3. Accuracy
                4. Encouraging professional help when appropriate

                Never claim to diagnose, treat, or replace a mental health professional.

                If the retrieved information is irrelevant, ignore it.
                If the user appears to be in immediate danger or at risk of self-harm, encourage contacting local emergency services, crisis resources, or a trusted person immediately.
                """
            }
        ]

    def perform_task(self, user_message, results=None):

        # Store user message
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        # Keep memory bounded
        self.messages = [self.messages[0]] + self.messages[-10:]

        # ==========================================
        # Build RAG context ONLY if results exist
        # ==========================================

        retrieved_context = ""

        if results:   # <- important check
            for i, result in enumerate(results, start=1):
                retrieved_context += f"""
                                        Document {i}

                                        Context:
                                        {result.payload.get('context', '')}

                                        Response:
                                        {result.payload.get('response', '')}

                                        ----------------------------------------
                                        """

        # ==========================================
        # Build final prompt
        # ==========================================

        user_content = f"""
                        User Question:
                        {user_message}
                        """

        # Only inject RAG section if not empty
        if retrieved_context.strip():
            user_content += f"""

                            Retrieved Knowledge Base Results:
                            {retrieved_context}

                            Instructions:
                            - Use retrieved information if relevant.
                            - Do not copy verbatim.
                            - If irrelevant, ignore it.
                            """

        else:
            user_content += """

                            Instructions:
                            - No external knowledge base provided.
                            - Answer directly using your general capabilities.
                            """

        generation_messages = self.messages.copy()
        generation_messages.append({
            "role": "user",
            "content": user_content
        })

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=generation_messages,
            temperature=0.7,
            max_completion_tokens=2048,
            stream=False
        )

        assistant_reply = completion.choices[0].message.content

        self.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })

        self.messages = [self.messages[0]] + self.messages[-10:]

        return assistant_reply




class QueryRewriter:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("LLM_API_KEY")
        )

        self.model = WEAK_MODEL

    def rewrite(self, user_query: str, chat_history: str = "", language: str = "") -> str:

        system_prompt = """
                        You rewrite search queries for a RAG system.

                        Rules:
                        - Preserve intent.
                        - Do not answer the query.
                        - Do not explain your reasoning.
                        - Resolve references using chat history.
                        - Return only the rewritten query.
                        """

        user_prompt = f"""
                        Chat History:
                        {chat_history}

                        Current User Query:
                        {user_query}
                        """

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0,
            max_completion_tokens=1024
        )

        content = completion.choices[0].message.content

        return content.strip()

import os
from groq import Groq

LANG_MAP = {
    "pt": "Portuguese",
    "bg": "Bulgarian",
    "zh": "Chinese",
    "th": "Thai",
    "ru": "Russian",
    "pl": "Polish",
    "ur": "Urdu",
    "sw": "Swahili",
    "tr": "Turkish",
    "es": "Spanish",
    "ar": "Arabic",
    "it": "Italian",
    "hi": "Hindi",
    "de": "German",
    "el": "Greek",
    "nl": "Dutch",
    "fr": "French",
    "vi": "Vietnamese",
    "en": "English",
    "ja": "Japanese",
}


class TranslationAgent:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("LLM_API_KEY")
        )
        self.model = WEAK_MODEL

    def _call_llm(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise translation engine."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()

    def to_english(self, text: str, code: str) -> str:
        if code == "en":
            return text  # No translation needed
        source_lang = LANG_MAP.get(code, code)

        prompt = f"""
                Translate the following text from {source_lang} to English.

                Rules:
                - Preserve meaning exactly
                - Do not explain
                - Output only the translation

                Text:
                {text}
                """
        return self._call_llm(prompt)

    def from_english(self, text: str, code: str) -> str:
        if code == "en":
            return text  # No translation needed
        target_lang = LANG_MAP.get(code, code)

        prompt = f"""
                Translate the following text from English to {target_lang}.

                Rules:
                - Preserve meaning exactly
                - Do not explain
                - Output only the translation

                Text:
                {text}
                """
        return self._call_llm(prompt)