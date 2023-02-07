import uuid

from pydantic import Field, validator

from models.base import JSONModel

NAMESPACE_ID = uuid.UUID("6ba7b816-9dad-11d1-80b4-00c04fd430c8")


class Movie(JSONModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    duration: int = 0

    @validator("id")
    def valid_id(cls, value):
        try:
            uuid.UUID(value)
            return value
        except ValueError:
            return str(uuid.uuid5(namespace=NAMESPACE_ID, name=value))

    @validator("duration")
    def duration_ge_zero(cls, value) -> int:
        if value >= 0:
            return value

        raise ValueError('"duration" must be greater than zero')
