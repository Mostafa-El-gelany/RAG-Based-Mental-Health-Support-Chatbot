from ..llm_service.llm.llm_agents import Agent, QueryRewriter, TranslationAgent
from ..intent_classifier.classifier import IntentClassifier
from ..Language_Detection.detector import LanguageDetector
from ..rag_system.rag.rag_agent import Rag
from ..emotion_classifier.classifier.emotion_classifier_agent import EmotionAgent
print('Importing Chat Engine...')
class ChatEngine:
    def __init__(self):
        print('Initializing Chat Engine...')
        self.rag_agent = Rag()
        self.llm_agent = Agent()
        self.translation_agent = TranslationAgent()
        self.rewriter = QueryRewriter()
        self.classifier = IntentClassifier()
        self.language_detector = LanguageDetector()
        self.emotion_agent = EmotionAgent()

    def process_message(self, user_message: str, top_k: int = 3):
        detected_language = self.language_detector.predict_top_k(user_message, k=5)
        if 'en' in dict(detected_language):
            detected_language = 'en'
        else:
            detected_language = detected_language[0]
        translated_prompt = self.translation_agent.to_english(user_message, detected_language)
        emotion = self.emotion_agent.predict(translated_prompt)
        intent = self.classifier.predict(translated_prompt, emotion)

        rewritten_query = translated_prompt
        results = []

        if intent == "asking_mental_health_question":
            rewritten_query = self.rewriter.rewrite(
                translated_prompt,
                language=detected_language,
            )
            results = self.rag_agent.search_top_k(rewritten_query, top_k=top_k)

        assistant_response = self.llm_agent.perform_task(user_message, results or None)
        assistant_response = self.translation_agent.from_english(assistant_response, detected_language)

        return {
            "user_message": user_message,
            "detected_language": detected_language,
            "translated_prompt": translated_prompt,
            "intent": intent,
            "rewritten_query": rewritten_query,
            "results": results,
            "assistant_response": assistant_response,
            "emotion": emotion
        }
