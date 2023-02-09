import uuid
from models.base import BaseMixin
from pydantic import Field
from typing import Any


class Recommendation(BaseMixin):
    user_id: uuid.UUID
    movies_id: list[uuid.UUID] = Field(default=[])

    def serializable_dict(self) -> dict[str, Any]:
        return {
            'user_id': str(self.user_id),
            'movies_id': map(lambda x: str(x), self.movies_id)
        }
