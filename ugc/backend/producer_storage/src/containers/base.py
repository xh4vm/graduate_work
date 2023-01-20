from typing import Optional, Type

from dependency_injector import containers, providers

from ..services.producer.base import BaseProducer


class ServiceFactory(providers.Factory):
    provided_type: Optional[Type] = BaseProducer


class BaseContainer(containers.DeclarativeContainer):
    value_serializer = providers.Dependency(instance_of=object)
    key_serializer = providers.Dependency(instance_of=object)
