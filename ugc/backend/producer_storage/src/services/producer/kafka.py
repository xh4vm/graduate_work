from pydantic.main import ModelMetaclass
from aiokafka import AIOKafkaProducer

from .base import BaseProducer
from src.resources.serializer import Serializer
from src.core.config import CONFIG


class KafkaProducer(BaseProducer):
    def __init__(self, key_serializer: Serializer, value_serializer: Serializer) -> None:
        self.producer = AIOKafkaProducer(bootstrap_servers=CONFIG.KAFKA.SERVERS,
            key_serializer=key_serializer, value_serializer=value_serializer)

    async def __aenter__(self):
        await self.producer.start()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.producer.stop()

    async def produce(
        self, topic: str, key: str = None, value: ModelMetaclass = None, partition: int = None, timestamp: int = None
    ) -> None:

        await self.producer.send_and_wait(
            topic=topic, key=key, value=value, partition=partition, timestamp_ms=timestamp
        )
