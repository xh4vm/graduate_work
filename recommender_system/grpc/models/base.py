import uuid
import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """ Get from json."""

    return orjson.dumps(v, default=default).decode()


class BaseMixin(BaseModel):
    """ Class parent for models. """

    class Config:

        json_loads = orjson.loads
        json_dumps = orjson_dumps
        cache_free = False

class UUIDModelMixin(BaseModel):
    id: uuid.UUID

    @property
    def id_str(self) -> str:
        return str(self.id)
