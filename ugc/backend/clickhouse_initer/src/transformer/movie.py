import random
from typing import Iterable, Any

from models.movie import Movie
from transformer.base import BaseTransformer


class MovieTransformer(BaseTransformer):
    def transform(self, raw_data: Iterable[dict[str, Any]]) -> Iterable[Movie]:
        for data in raw_data:
            movie_id = data.get("id") or data.get("movie_id")
            movie_duration = data.get("duration") or random.randint(1, 3) * 60 * 60 * 60
            movie = Movie(id=movie_id, duration=movie_duration)
            yield movie
