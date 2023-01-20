import enum
from abc import ABC
from typing import Any
from pydantic import Field

from .base import JSONModel


class AvroSchema(ABC):
    __avro_types__ = {
        'str': 'string',
        'int': 'long',
        'uuid': 'string',
        'date': 'int',
        'time': 'int',
        'datetime': 'long',
        'EventType': 'string',
    }

    @classmethod
    def schema(cls) -> dict[str, Any]:
        fields = [
            {'name': field.alias, 'type': cls.__avro_types__.get(field.type_.__name__)}
            for field in cls.__fields__.values()
        ]
        return {'name': cls.__name__, 'type': 'record', 'fields': fields}


class EventType(str, enum.Enum):
    START = 'start'
    STOP = 'stop'
    PROCESS = 'process'


class MovieFrameDatagram(JSONModel):
    movie_id: str
    frame_time: int
    event_type: EventType = Field(default=EventType.PROCESS)


class MovieFrame(AvroSchema, MovieFrameDatagram):
    pass
