import uuid
from pydantic import Field, validator
from random import randint

from src.models.base import JSONModel


NAMESPACE_ID = uuid.UUID('6ba7b816-9dad-11d1-80b4-00c04fd430c8')


class MovieFrameDatagram(JSONModel):
    user_id: str
    movie_id: str
    metric: float

    @validator('user_id', 'movie_id')
    def valid_uuid(value: str):    
        try:
            uuid.UUID(value)
            return value
        except ValueError:
            return str(uuid.uuid5(namespace=NAMESPACE_ID, name=value))

    @validator('metric')
    def frame_time_ge_zero(cls, value: int) -> int:
        if value >= 0:
            return value

        raise ValueError('"metric" must be greater than zero')


class MovieMetadata(JSONModel):
    id: str
    duration: int

    @validator('id')
    def valid_uuid(value: str):    
        try:
            uuid.UUID(value)
            return value
        except ValueError:
            return str(uuid.uuid5(namespace=NAMESPACE_ID, name=value))

    @validator('duration')
    def duration_ge_zero(cls, value: int) -> int:
        if value >= 0:
            return value

        raise ValueError('"duration" must be greater than zero')


class FakeMovieMetadata(MovieMetadata):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    duration: int = Field(default_factory=lambda: randint(1, 3) * 60 * 60 * 60)
