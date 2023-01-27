import orjson
from typing import Callable, Any
from pydantic.main import ModelMetaclass

from dependency_injector import resources

from .serializer import Serializer

class JSONSerializerResource(resources.Resource):
    def init(
        self,
        to_dict: Callable[[ModelMetaclass], dict[str, Any]] = None,
    ) -> Serializer:
        return Serializer(lambda obj: orjson.dumps(to_dict(obj)))
