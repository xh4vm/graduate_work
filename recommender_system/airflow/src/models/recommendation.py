import uuid
from models.base import JSONModel
from pydantic import Field
from typing import Any, List, Dict


class Recommendation(JSONModel):
    user_id: uuid.UUID
    movies_id: List[uuid.UUID] = Field(default=[])

    def serializable_dict(self) -> Dict[str, Any]:
        return {
            'user_id': str(self.user_id),
            'movies_id': map(lambda x: str(x), self.movies_id)
        }
