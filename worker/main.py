import asyncio
import httpx
import json
import os
from typing import List, Optional, Set
from pydantic import BaseModel
from enum import Enum


# ==================== МОДЕЛИ ====================
class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ReviewStatus(str, Enum):
    NEW = "new"
    PROCESSED = "processed"


class Review(BaseModel):
    id: int
    author: str
    content: str
    rating: Optional[int] = None
    status: ReviewStatus
    sentiment: Optional[Sentiment] = None


class CommentCreate(BaseModel):
    review_id: int
    author: str
    content: str
    is_ai_generated: bool = True


# ==================== КОНФИГ ====================
class Config:
    TARGET_SITE_URL = os.getenv("TARGET_SITE_URL", "http://app:8000")
    WORKER_API_TOKEN = os.getenv("WORKER_API_TOKEN", "change-me")
    WORKER_POLL_INTERVAL = int(os.getenv("WORKER_POLL_INTERVAL", "10"))
    STATE_FILE_PATH = os.getenv("STATE_FILE_PATH", "data/state.json")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    AI_AUTHOR_NAME = os.getenv("AI_AUTHOR_NAME", "AI Assistant")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_USER_CHAT_ID = os.getenv("TELEGRAM_USER_CHAT_ID")


config = Config()


# ==================== CLIENT ====================
class APIClient:
    def __init__(self):
        self.base_url = config.TARGET_SITE_URL.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {config.WORKER_API_TOKEN}",
            "Content-Type": "application/json"
        }

    async def get_new_reviews(self) -> List[Review]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/reviews",
                    params={"status": "new", "limit": 100},
                    headers=self.headers
                )
                if response.status_code == 200:
                    data = response.json()
                    return [Review(**item) for item in data]
                return []
        except Exception as e:
            print(f"Ошибка получения отзывов: {e}")
            return []

    async def update_review(self, review_id: int, status: ReviewStatus, sentiment: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/api/reviews/{review_id}",
                    json={"status": status.value, "sentiment": sentiment},
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Ошибка обновления отзыва: {e}")
            return False

    async def create_comment(self, review_id: int, author: str, content: str) -> bool:
        try:
            comment = CommentCreate(
                review_id=review_id,
                author=author,
                content=content,
                is_ai_generated=True
            )
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/comments",
                    json=comment.model_dump(),
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Ошибка создания комментария: {e}")
            return False


# ==================== STATE ====================
class StateManager:
    def __init__(self):
        self.state_file_path = config.STATE_FILE_PATH
        self.processed_reviews: Set[int] = set()
        self.load()

    def load(self):
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, 'r') as f:
                    data = json.load(f)
                    self.processed_reviews = set(data.get('processed_reviews', []))
                print(f"Загружено {len(self.processed_reviews)} обработанных отзывов")
            except Exception as e:
                print(f"Ошибка загрузки состояния: {e}")

    def save(self):
        os.makedirs(os.path.dirname(self.state_file_path), exist_ok=True)
        try:
            with open(self.state_file_path, 'w') as f:
                json.dump({'processed_reviews': list(self.processed_reviews)}, f)
        except Exception as e:
            print(f"Ошибка сохранения состояния: {e}")

    def is_processed(self, review_id: int) -> bool:
        return review_id in self.processed_reviews

    def mark_processed(self, review_id: int):
        self.processed_reviews.add(review_id)
        self.save()


# ==================== PROCESSOR ====================
class ReviewProcessor:
    async def analyze_sentiment(self, text: str) -> tuple:
        """Определить тональность и сгенерировать ответ"""
        text_lower = text.lower()

        positive_words = [
            'спасибо', 'отлично', 'хорошо', 'прекрасно', 'нравится',
            'супер', 'класс', 'замечательно', 'великолепно',
            'лучшие', 'понравилось', 'доволен', 'довольна', 'хороший',
            'отличная', 'суперский', 'круто', 'обращусь еще', 'топ',
            'восторг', 'благодарю', 'помогли'
        ]

        negative_words = [
            'плохо', 'ужасно', 'не работает', 'ошибка', 'баг', 'проблема',
            'отвратительно', 'ужас', 'кошмар', 'разочарован', 'не буду',
            'никогда', 'ничего не сделали', 'не приду', 'не советую',
            'позор', 'отвратительная', 'ужасная', 'сломали', 'кошмарная',
            'не обращусь', 'недоволен', 'недовольна', 'бесполезно',
            'зря', 'разочарование', 'не помогли', 'не справились'
        ]

        neutral_words = [
            'нормально', 'обычно', 'так себе', 'ничего особенного',
            'средне', 'неплохо', 'посредственно', 'терпимо',
            'как обычно', 'без восторга', 'нейтрально'
        ]

        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        neutral_score = sum(1 for word in neutral_words if word in text_lower)

        if positive_score > negative_score and positive_score > neutral_score:
            sentiment = "positive"
            reply = "Спасибо за положительный отзыв! Мы рады, что вам нравится."
        elif negative_score > positive_score and negative_score > neutral_score:
            sentiment = "negative"
            reply = "Спасибо за ваш отзыв. Мы работаем над улучшением сервиса."
        elif neutral_score > 0:
            sentiment = "neutral"
            reply = "Спасибо за ваш отзыв. Мы учтём ваше мнение."
        else:
            sentiment = "neutral"
            reply = "Спасибо за ваш отзыв!"

        return sentiment, reply


# ==================== TELEGRAM ====================
class TelegramNotifier:
    def __init__(self):
        self.enabled = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_USER_CHAT_ID)

    async def send_notification(self, review_author: str, review_content: str, sentiment: str):
        if not self.enabled:
            return

        sentiment_emoji = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(sentiment, "📝")
        message = f"{sentiment_emoji} *Новый отзыв!*\n\n*Автор:* {review_author}\n*Тональность:* {sentiment}\n\n*Текст:*\n{review_content[:500]}"

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={"chat_id": config.TELEGRAM_USER_CHAT_ID, "text": message, "parse_mode": "Markdown"}
                )
                print(f"Уведомление отправлено в Telegram")
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")


# ==================== WORKER ====================
class Worker:
    def __init__(self):
        self.client = APIClient()
        self.processor = ReviewProcessor()
        self.state = StateManager()
        self.notifier = TelegramNotifier()
        self.running = True

    async def process_review(self, review):
        print(f"Обработка отзыва #{review.id} от {review.author}")

        sentiment, reply = await self.processor.analyze_sentiment(review.content)
        print(f"  Тональность: {sentiment}")

        await self.notifier.send_notification(review.author, review.content, sentiment)

        success = await self.client.create_comment(review.id, config.AI_AUTHOR_NAME, reply)
        if success:
            print(f"  Ответ создан: {reply[:50]}...")
        else:
            print(f"  Ошибка создания ответа")

        await self.client.update_review(review.id, ReviewStatus.PROCESSED, sentiment)
        self.state.mark_processed(review.id)
        print(f"  Отзыв #{review.id} обработан\n")

    async def run_once(self):
        print("Проверка новых отзывов...")
        reviews = await self.client.get_new_reviews()
        print(f"Найдено {len(reviews)} новых отзывов")

        for review in reviews:
            if self.state.is_processed(review.id):
                continue
            if "AI Assistant" in review.author or config.AI_AUTHOR_NAME in review.author:
                print(f"Пропускаем отзыв от AI: #{review.id}")
                self.state.mark_processed(review.id)
                continue
            await self.process_review(review)

    async def run(self):
        print(f"Worker запущен")
        print(f"Целевой сайт: {config.TARGET_SITE_URL}")
        print(f"Интервал опроса: {config.WORKER_POLL_INTERVAL} сек")

        while self.running:
            try:
                await self.run_once()
            except Exception as e:
                print(f"Ошибка: {e}")
            await asyncio.sleep(config.WORKER_POLL_INTERVAL)


if __name__ == "__main__":
    worker = Worker()
    try:
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        print("\nWorker остановлен")