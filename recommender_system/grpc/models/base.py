import uuid
from datetime import datetime
from pydantic import BaseModel


class UUIDModelMixin(BaseModel):
    id: uuid.UUID

    @property
    def id_str(self) -> str:
        return str(self.id)


class TimeStampedModelMixin(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None
