import json
import os
from typing import Set


class StateManager:
    """Управление состоянием обработанных отзывов"""

    def __init__(self, state_file_path: str):
        self.state_file_path = state_file_path
        self.processed_reviews: Set[int] = set()
        self.load()

    def load(self):
        """Загрузить состояние из файла"""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, 'r') as f:
                    data = json.load(f)
                    self.processed_reviews = set(data.get('processed_reviews', []))
                print(f"Загружено {len(self.processed_reviews)} обработанных отзывов")
            except Exception as e:
                print(f"Ошибка загрузки состояния: {e}")

    def save(self):
        """Сохранить состояние в файл"""
        os.makedirs(os.path.dirname(self.state_file_path), exist_ok=True)
        try:
            with open(self.state_file_path, 'w') as f:
                json.dump({'processed_reviews': list(self.processed_reviews)}, f)
        except Exception as e:
            print(f"Ошибка сохранения состояния: {e}")

    def is_processed(self, review_id: int) -> bool:
        """Проверить, обработан ли отзыв"""
        return review_id in self.processed_reviews

    def mark_processed(self, review_id: int):
        """Отметить отзыв как обработанный"""
        self.processed_reviews.add(review_id)
        self.save()