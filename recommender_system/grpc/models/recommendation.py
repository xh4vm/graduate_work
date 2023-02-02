import uuid
from models.base import UUIDModelMixin, TimeStampedModelMixin

class Recommendation(UUIDModelMixin, TimeStampedModelMixin):
    user_id: uuid.UUID
    movies_id: list[uuid.UUID]
