from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class ReviewStatus(str, Enum):
    NEW = "new"
    PROCESSED = "processed"

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class ReviewBase(BaseModel):
    author: str
    content: str
    rating: Optional[int] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    status: Optional[ReviewStatus] = None
    sentiment: Optional[Sentiment] = None

class ReviewResponse(ReviewBase):
    id: int
    status: ReviewStatus
    sentiment: Optional[Sentiment] = None
    created_at: datetime
    updated_at: Optional[datetime] = None   # <-- сделали Optional

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    review_id: int
    author: str
    content: str
    is_ai_generated: bool = False