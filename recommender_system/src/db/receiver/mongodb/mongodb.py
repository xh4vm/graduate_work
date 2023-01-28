from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pyspark.sql import SparkSession

from src.db.receiver.base import AsyncDBStorage
from src.utilities.utilities import test_connection


class AsyncMongoDB(AsyncDBStorage):
    db: AsyncIOMotorDatabase = None

    def __init__(self):
        self.cl: AsyncIOMotorClient | None = None

    def init_db(self, db_name):
        self.db = self.cl[db_name]

    @test_connection
    async def exec_command(self, db_name: str, command: dict, *args, **kwargs):
        res = await self.cl[db_name].command(command)
        return res

    @test_connection
    async def aggregate(
            self,
            collection: str,
            match: dict = None,
            group: dict = None,
            lookup: dict = None,
            project: dict = None,
            limit: dict = None,
            skip: dict = None
    ):

        pipeline = [command_obj for command_obj in (lookup, project, match, group, skip, limit) if command_obj]
        cursor = self.db.get_collection(collection).aggregate(pipeline=pipeline)
        result = [doc async for doc in cursor]

        return result

    @test_connection
    async def insert_one(self, collection: str, data: dict,  *args, **kwargs):
        try:
            return None, await self.db.get_collection(collection).insert_one(data)
        except DuplicateKeyError as err:
            return err, None

    @test_connection
    async def update_one(self, collection: str, find: dict, update: dict, *args, **kwargs):
        result = await self.db.get_collection(collection).find_one_and_update(
            find,
            update,
            return_document=ReturnDocument.AFTER
        )
        return result

    @test_connection
    async def delete_one(self, collection: str, data: dict, *args, **kwargs):
        result = await self.db.get_collection(collection).find_one_and_delete(data)
        return result

    @test_connection
    async def delete_many(self, collection: str, data: dict, *args, **kwargs):
        result = await self.db.get_collection(collection).delete_many(data)
        return result

    @test_connection
    async def find(self, collection: str, query: dict, options: dict = None, *args, **kwargs):
        options = options or {}
        cursor = self.db.get_collection(collection).find(query, {}, **options)

        return [doc async for doc in cursor]

    @test_connection
    async def count(self, collection: str, query: dict, *args, **kwargs) -> int:
        return await self.db.get_collection(collection).count_documents(query)

    @test_connection
    async def drop_collections(self):
        for collection in self.db.list_collection_names():
            self.db.drop_collection(collection)


mdb = AsyncMongoDB()


async def get_mongodb() -> AsyncMongoDB:
    """ Get mongodb object. """

    return mdb
