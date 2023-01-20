from dependency_injector import containers

from ..services.producer.kafka import KafkaProducer
from .base import BaseContainer, ServiceFactory


class ServiceContainer(BaseContainer):

    wiring_config = containers.WiringConfiguration(modules=['..api.v1.movies'])

    kafka_producer = ServiceFactory(
        KafkaProducer, key_serializer=BaseContainer.key_serializer, value_serializer=BaseContainer.value_serializer
    )
