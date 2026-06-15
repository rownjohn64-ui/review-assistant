import httpx
from worker.config import config


class TelegramNotifier:
    def __init__(self):
        self.enabled = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_USER_CHAT_ID)
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_USER_CHAT_ID

    async def send_notification(self, review_author: str, review_content: str, sentiment: str):
        """Отправить уведомление о новом отзыве в Telegram"""
        if not self.enabled:
            return

        sentiment_emoji = {
            "positive": "😊",
            "negative": "😞",
            "neutral": "😐"
        }.get(sentiment, "📝")

        message = f"""
{sentiment_emoji} *Новый отзыв!*

*Автор:* {review_author}
*Тональность:* {sentiment}

*Текст отзыва:*
{review_content[:500]}

---
🤖 AI скоро ответит на этот отзыв.
"""

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                )
                print(f"Уведомление отправлено в Telegram")
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")