import enum
from pydantic import Field

from .base import JSONModel


class EventType(str, enum.Enum):
    STARTING = 'starting'
    STOPPED = 'stopped'
    VIEWED = 'viewed'


class Event(JSONModel):
    type: EventType = Field(default=EventType.VIEWED)
    timestamp: int
    generated_after: int | None = Field(default=None)


class MovieFrameDatagram(JSONModel):
    movie_id: str
    frame_time: int
    event: Event


class MovieFrame(MovieFrameDatagram):
    pass
