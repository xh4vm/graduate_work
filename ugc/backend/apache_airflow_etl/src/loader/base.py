from abc import ABC
from typing import Iterator


class BaseLoader(ABC):
    def insert(self, data: Iterator, **kwargs) -> None:
        pass
