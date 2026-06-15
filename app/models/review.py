from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.base import Base
from app.schemas import ReviewStatus, Sentiment
import enum

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.NEW)
    sentiment = Column(SQLEnum(Sentiment), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, nullable=False)
    author = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_ai_generated = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())