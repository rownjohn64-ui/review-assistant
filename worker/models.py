from pydantic import BaseModel
from typing import Optional
from enum import Enum

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

class ReviewUpdate(BaseModel):
    status: Optional[ReviewStatus] = None
    sentiment: Optional[Sentiment] = None