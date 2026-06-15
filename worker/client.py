import httpx
from typing import List, Optional
from models import Review, CommentCreate, ReviewUpdate, ReviewStatus


class APIClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
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

    async def get_comments(self, review_id: int) -> List[dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/comments/{review_id}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception as e:
            print(f"Ошибка получения комментариев: {e}")
            return []