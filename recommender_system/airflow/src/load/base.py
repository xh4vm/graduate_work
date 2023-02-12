from abc import ABC, abstractmethod
from pydantic.main import ModelMetaclass
from typing import Iterator, List, Any


class BaseClient(ABC):
    @property
    @abstractmethod
    def conn(self):
        '''Клиент БД'''


class BaseLoader(ABC):

    @abstractmethod
    def load(self, data: Iterator[ModelMetaclass], **kwargs) -> List[Any]:
        '''Метод '''
