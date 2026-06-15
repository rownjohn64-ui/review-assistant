import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from client import APIClient
from processor import ReviewProcessor
from state import StateManager
from telegram_bot import TelegramNotifier
from models import ReviewStatus


class Worker:
    def __init__(self):
        self.client = APIClient(config.TARGET_SITE_URL, config.WORKER_API_TOKEN)
        self.processor = ReviewProcessor()
        self.state = StateManager(config.STATE_FILE_PATH)
        self.notifier = TelegramNotifier()
        self.running = True

    async def process_review(self, review):
        print(f"Обработка отзыва #{review.id} от {review.author}")

        sentiment, reply = await self.processor.analyze_sentiment(review.content)
        print(f"  Тональность: {sentiment}")

        await self.notifier.send_notification(review.author, review.content, sentiment)

        success = await self.client.create_comment(
            review.id,
            config.AI_AUTHOR_NAME,
            reply
        )

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
        print()

        while self.running:
            try:
                await self.run_once()
            except Exception as e:
                print(f"Ошибка: {e}")

            await asyncio.sleep(config.WORKER_POLL_INTERVAL)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    worker = Worker()
    try:
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        print("\nWorker остановлен")
        worker.stop()