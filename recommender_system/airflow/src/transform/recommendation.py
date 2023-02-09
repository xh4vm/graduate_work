from typing import Iterator, Any, Dict

from src.transform.base import BaseTransformer
from src.models.recommendation import Recommendation


class RecommendationTransformer(BaseTransformer):

    def transform(self, raw: Iterator[Dict[str, Any]], to_dict: bool = False) -> Iterator[Any]:
        for raw_elem in raw:
            elem = Recommendation(**raw_elem)
            yield elem.dict() if to_dict else elem
