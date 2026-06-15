from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.review import Review, Comment
from app.schemas import ReviewCreate, ReviewResponse, ReviewUpdate, CommentCreate, ReviewStatus, Sentiment

router = APIRouter(prefix="/api", tags=["reviews"])


@router.post("/reviews", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, db: AsyncSession = Depends(get_db)):
    db_review = Review(**review.model_dump())
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review


@router.get("/reviews", response_model=list[ReviewResponse])
async def get_reviews(
        status: ReviewStatus = None,
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    query = select(Review)
    if status:
        query = query.where(Review.status == status)
    query = query.order_by(Review.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.patch("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: int, update: ReviewUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)

    await db.commit()
    await db.refresh(review)
    return review


@router.post("/comments")
async def create_comment(comment: CommentCreate, db: AsyncSession = Depends(get_db)):
    db_comment = Comment(**comment.model_dump())
    db.add(db_comment)
    await db.commit()
    return {"status": "ok", "id": db_comment.id}


@router.get("/comments/{review_id}")
async def get_comments(review_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).where(Comment.review_id == review_id))
    comments = result.scalars().all()
    return comments