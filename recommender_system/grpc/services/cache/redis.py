
import backoff
from typing import Any

import orjson
from aioredis import Redis, create_redis_pool
from aioredis.errors import RedisError
from core.config import RedisSettings, BACKOFF_CONFIG, logger

from .base import BaseCache


def is_alive(conn: Redis) -> bool:
    try:
        conn.ping()
        return True
    except RedisError:
        return False



class RedisCache(BaseCache):
    def __init__(self, settings: RedisSettings, conn: Redis = None):
        self._settings = settings
        self._conn = conn

    @backoff.on_exception(**BACKOFF_CONFIG, logger=logger)
    async def _reconnection(self) -> Redis:
        if self._conn is not None:
            self._conn.close()
        
        return await create_redis_pool((self._settings.HOST, self._settings.PORT), minsize=10, maxsize=20)

    @property
    async def conn(self) -> Redis:
        if self._conn is None or not is_alive(self._conn):
            return await self._reconnection()

        return self._conn

    async def get(self, key: str, default_value: str | None = None) -> str | None:
        data = await (await self.conn).get(key)

        if data is None:
            return default_value

        return orjson.loads(data)

    async def set(self, key: str, data: Any) -> None:
        await (await self.conn).set(key=key, value=orjson.dumps(data), expire=self._settings.CACHE_EXPIRE)
