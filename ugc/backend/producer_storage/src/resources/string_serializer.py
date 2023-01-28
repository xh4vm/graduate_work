from dependency_injector import resources

from .serializer import Serializer


class StringSerializerResource(resources.Resource):
    def init(self, codec: str, *args, **kwargs) -> Serializer:
        return Serializer(lambda str: str.encode(codec))
