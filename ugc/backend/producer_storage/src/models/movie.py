import enum
from pydantic import Field
from datetime import datetime

from .base import JSONModel


class EventType(str, enum.Enum):
    STARTING = 'starting'
    STOPPED = 'stopped'
    VIEWED = 'viewed'


class Event(JSONModel):
    type: EventType = Field(default=EventType.VIEWED)
    timestamp: int = Field(default_factory=lambda : int(datetime.utcnow().timestamp()))
    generated_after: int | None = Field(default=None)


class MovieFrameDatagram(JSONModel):
    movie_id: str
    frame_time: int
    event: Event


class MovieFrame(MovieFrameDatagram):
    pass
