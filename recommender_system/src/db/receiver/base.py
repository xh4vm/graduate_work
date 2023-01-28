from abc import ABC, abstractmethod
from pyspark.sql import SparkSession


class AsyncDBStorage(ABC):

    @abstractmethod
    async def exec_command(self, db_name: str, command: dict, *args, **kwargs):
        pass

    @abstractmethod
    async def insert_one(self, collection: str, data: dict,  *args, **kwargs):
        pass

    @abstractmethod
    async def update_one(self, collection: str, find: dict, update: dict, *args, **kwargs):
        pass

    @abstractmethod
    async def delete_one(self, collection: str, data: dict, *args, **kwargs):
        pass

    @abstractmethod
    async def find(self, collection: str, query: dict, options: dict, *args, **kwargs):
        pass

    @abstractmethod
    async def drop_collections(self):
        pass

    @abstractmethod
    async def count(self, collection: str, query: dict, *args, **kwargs) -> int:
        pass
