from abc import ABC, abstractmethod
from typing import Iterator, Any


class BaseExtractor(ABC):

    @abstractmethod
    def extract(self) -> Iterator[Any]:
        '''Метод извлечения данных'''
