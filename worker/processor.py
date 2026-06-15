import httpx
from worker.config import config
from typing import Tuple
import random


class ReviewProcessor:
    def __init__(self):
        self.openai_enabled = bool(config.OPENAI_API_KEY)

    async def analyze_sentiment(self, text: str) -> Tuple[str, str]:
        """Определить тональность отзыва и сгенерировать ответ"""

        if self.openai_enabled and config.OPENAI_API_KEY:
            try:
                sentiment, reply = await self._analyze_with_openai(text)
                if sentiment and reply:
                    return sentiment, reply
            except Exception as e:
                print(f"OpenAI error: {e}")

        return self._fallback_analyze(text)

    async def _analyze_with_openai(self, text: str) -> Tuple[str, str]:
        """Анализ через OpenAI API"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": """
                        Ты — AI-ассистент, который анализирует отзывы.
                        Определи тональность отзыва: positive (положительный), negative (отрицательный) или neutral (нейтральный).
                        Затем сгенерируй вежливый ответ на отзыв.

                        Верни JSON в формате:
                        {"sentiment": "positive/negative/neutral", "reply": "текст ответа"}
                        """},
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0.7
                }
            )

            if response.status_code == 200:
                import json
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                data = json.loads(content)
                return data.get("sentiment", "neutral"), data.get("reply", "Спасибо за ваш отзыв!")
            else:
                return "neutral", "Спасибо за ваш отзыв!"

    def _fallback_analyze(self, text: str) -> Tuple[str, str]:
        """Fallback-логика при отсутствии OpenAI"""
        text_lower = text.lower()

        positive_words = ['спасибо', 'отлично', 'хорошо', 'прекрасно', 'нравится', 'отличный']
        negative_words = ['плохо', 'ужасно', 'не работает', 'ошибка', 'баг', 'проблема']

        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)

        if positive_score > negative_score:
            sentiment = "positive"
            reply = "Спасибо за положительный отзыв! Мы рады, что вам нравится."
        elif negative_score > positive_score:
            sentiment = "negative"
            reply = "Спасибо за ваш отзыв. Мы работаем над улучшением сервиса."
        else:
            sentiment = "neutral"
            reply = "Спасибо за ваш отзыв!"

        return sentiment, reply