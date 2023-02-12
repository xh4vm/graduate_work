from typing import Iterator, Any, Dict

from loguru import logger
from src.transform.base import BaseTransformer
from src.models.movie import MovieMetadata, FakeMovieMetadata


class MovieFrameTransformer(BaseTransformer):

    def transform(self, raw: Iterator[Dict[str, Any]], to_dict: bool = False) -> Iterator[Any]:
        for raw_elem in raw:
            elem = MovieMetadata(**raw_elem)
            yield elem.dict() if to_dict else elem


class FakeMovieFrameTransformer(BaseTransformer):

    def transform(self, raw: Iterator[Dict[str, Any]], to_dict: bool = False) -> Iterator[Any]:
        for raw_elem in raw:
            elem = FakeMovieMetadata(**raw_elem)
            yield elem.dict() if to_dict else elem
