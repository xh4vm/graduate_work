import enum
from pydantic import Field, validator
from datetime import datetime
from typing import Any

from .base import JSONModel


class EventType(str, enum.Enum):
    STARTING = 'starting'
    STOPPED = 'stopped'
    VIEWED = 'viewed'


class Event(JSONModel):
    type: EventType = Field(default=EventType.VIEWED)
    timestamp: int = Field(default_factory=lambda : int(datetime.utcnow().timestamp()))


class MovieFrameDatagram(JSONModel):
    movie_id: str
    frame_time: int
    event: Event

    @validator('frame_time')
    def frame_time_ge_zero(cls, value: int) -> int:
        if value >= 0:
            return value

        raise ValueError('"frame_time" must be greater than zero')


class MovieFrame(MovieFrameDatagram):
    pass
