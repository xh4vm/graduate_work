from abc import ABC, abstractmethod
from typing import Any, Iterable

from pydantic.main import ModelMetaclass


class BaseTransformer(ABC):
    @abstractmethod
    def transform(self, raw_data: Iterable[dict[str, Any]]) -> Iterable[ModelMetaclass]:
        pass
