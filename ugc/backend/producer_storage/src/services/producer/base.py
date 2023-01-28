from abc import ABC, abstractmethod


class BaseProducer(ABC):
    @abstractmethod
    def produce(self, **kwargs) -> None:
        """Публикование данных в хранилище"""
