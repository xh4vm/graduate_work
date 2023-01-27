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
    movie_duration: int
    event: Event

    @validator('movie_duration', 'frame_time')
    def frame_time_ge_zero(cls, value: int) -> int:
        if value >= 0:
            return value

        raise ValueError('"frame_time" and "movie_duration" must be greater than zero')

    @validator('movie_duration')
    def movie_duration_ge_frame_time(cls, value: int, values: dict[str, Any], **kwargs) -> int:
        if values.get('frame_time') is not None and value >= values.get('frame_time'):
            return value

        raise ValueError('"movie_duration" must be greater than "frame_time"')


class MovieFrame(MovieFrameDatagram):
    pass
