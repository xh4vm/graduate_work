from abc import ABC, abstractmethod, abstractproperty
from typing import Any


class BaseDB(ABC):
    @abstractproperty
    def conn(self):
        '''Клиент БД'''

    @abstractmethod
    def last(self, count: int, sorts: list[Any] | None = None, filter: dict[str, Any] | None = None, **kwargs):
        '''Метод получения {{count}} последних экземпляров'''

    @abstractmethod
    def last_one(self, sorts: list[Any] | None = None, filter: dict[str, Any] | None = None, **kwargs):
        '''Метод получения {{count}} последних экземпляров'''
