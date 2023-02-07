import backoff
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from services.storage.base import BaseDB
from core.config import DBSettings, logger, BACKOFF_CONFIG
from typing import Any


def is_alive(conn: AsyncIOMotorClient) -> bool:
    try:
        conn.server_info()
    except ServerSelectionTimeoutError as exception:
        logger.exception(exception)


class AsyncMongoDB(BaseDB):
    def __init__(self, settings: DBSettings, conn: AsyncIOMotorClient = None):
        self._settings: DBSettings = settings
        self._conn: AsyncIOMotorClient = conn

    @backoff.on_exception(**BACKOFF_CONFIG, logger=logger)
    def _reconnection(self) -> AsyncIOMotorClient:
        if self._conn is not None:
            self._conn.close()
        
        return AsyncIOMotorClient(
            f'{self._settings.DRIVER}://{self._settings.HOST}:{self._settings.PORT}',
            uuidRepresentation='standard'
        )

    @property
    def conn(self) -> AsyncIOMotorClient:
        if self._conn is None or not is_alive(self._conn):
            return self._reconnection()

        return self._conn

    def last(
        self,
        db_name: str,
        collection_name: str,
        count: int,
        filter: dict[str, Any] | None = None,
        sorts: list[Any] | None = None
    ):
        cursor = self.conn[db_name][collection_name].find(filter or {})
         
        if sorts is not None:
            cursor = cursor.sort(sorts)
        
        return cursor.limit(count)

    async def last_one(
        self,
        db_name: str,
        collection_name: str,
        filter: dict[str, Any] | None = None,
        sorts: list[Any] | None = None
    ) -> dict[str, Any]:
        async for elem in self.last(
            count=1,
            db_name=db_name,
            collection_name=collection_name,
            filter=filter,
            sorts=sorts
        ):
            return elem
