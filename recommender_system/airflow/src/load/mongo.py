import backoff
from pydantic.main import ModelMetaclass
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from load.base import BaseLoader
from loguru import logger
from core.config import DBSettings, BACKOFF_CONFIG
from typing import Iterator, List, Any


def is_alive(conn: AsyncIOMotorClient) -> bool:
    try:
        conn.server_info()
    except ServerSelectionTimeoutError as exception:
        logger.exception(exception)


class AsyncMongoLoader(BaseLoader):
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

    async def load(
        self,
        db_name: str,
        collection_name: str,
        data: Iterator[ModelMetaclass]
    ) -> List[Any]:
        cursor = self.conn[db_name][collection_name]
        result = await cursor.insert_many(data)
        return result.inserted_ids
