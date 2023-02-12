
import backoff
from typing import Any

import orjson
from redis.asyncio import Redis
from core.config import RedisSettings, BACKOFF_CONFIG, logger

from .base import BaseCache


class RedisCache(BaseCache):
    def __init__(self, settings: RedisSettings, conn: Redis = None):
        self._settings = settings
        self._conn = conn

    @backoff.on_exception(**BACKOFF_CONFIG, logger=logger)
    def _reconnection(self) -> Redis:
        if self._conn is not None:
            self._conn.close()

        return Redis(
            host=self._settings.HOST,
            port=self._settings.PORT,
            password=self._settings.PASSWORD
        )

    @property
    @backoff.on_exception(**BACKOFF_CONFIG, logger=logger)
    def conn(self) -> Redis:
        if self._conn is None:
            return self._reconnection()

        return self._conn

    @conn.setter
    @backoff.on_exception(**BACKOFF_CONFIG, logger=logger)
    def conn(self) -> Redis:
        return self

    async def get(self, key: str, default_value: str | None = None) -> str | None:
        data = await self.conn.get(key)

        if data is None:
            return default_value

        return orjson.loads(data)

    async def set(self, key: str, data: Any) -> None:
        await self.conn.set(name=key, value=orjson.dumps(data), ex=self._settings.CACHE_EXPIRE)
