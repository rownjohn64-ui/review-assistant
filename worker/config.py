import os
from dotenv import load_dotenv

load_dotenv()


class WorkerConfig:
    TARGET_SITE_URL = os.getenv("TARGET_SITE_URL", "http://app:8000")
    WORKER_API_TOKEN = os.getenv("WORKER_API_TOKEN", "change-me")
    WORKER_POLL_INTERVAL = int(os.getenv("WORKER_POLL_INTERVAL", "10"))
    STATE_FILE_PATH = os.getenv("STATE_FILE_PATH", "data/state.json")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    AI_AUTHOR_NAME = os.getenv("AI_AUTHOR_NAME", "AI Assistant")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_USER_CHAT_ID = os.getenv("TELEGRAM_USER_CHAT_ID")


config = WorkerConfig()