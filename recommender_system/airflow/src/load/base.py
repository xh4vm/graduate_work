from abc import ABC, abstractmethod, abstractproperty
from pydantic.main import ModelMetaclass
from typing import Iterator, List, Any


class BaseLoader(ABC):
    @abstractproperty
    def conn(self):
        '''Клиент БД'''

    @abstractmethod
    def load(self, data: Iterator[ModelMetaclass], **kwargs) -> List[Any]:
        '''Метод '''
