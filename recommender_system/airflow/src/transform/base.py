from abc import ABC, abstractmethod
from typing import Iterator, Any, Dict


class BaseTransformer(ABC):

    @abstractmethod
    def transform(self, raw: Iterator[Dict[str, Any]], to_dict: bool = False) -> Iterator[Any]:
        '''Метод трансформации данных'''
