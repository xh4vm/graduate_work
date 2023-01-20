from confluent_kafka.serialization import StringSerializer

from dependency_injector import resources


class StringSerializerResource(resources.Resource):
    def init(self, codec: str, *args, **kwargs) -> StringSerializer:
        return StringSerializer(codec)
