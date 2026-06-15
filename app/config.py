import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/reviews")
    WORKER_API_TOKEN = os.getenv("WORKER_API_TOKEN", "change-me")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    AI_AUTHOR_NAME = os.getenv("AI_AUTHOR_NAME", "AI Assistant")

config = Config()