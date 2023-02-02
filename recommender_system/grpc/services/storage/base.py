from abc import ABC, abstractmethod, abstractproperty
from typing import Any


class BaseDB(ABC):
    @abstractproperty
    def conn(self):
        '''Клиент БД'''

    @abstractmethod
    def one(self, filter: dict[str, Any] | None = None, **kwargs):
        '''Метод получения одного экземпляра данных'''
