from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.db.base import AsyncDBStorage
from src.utilities.utilities import test_connection


class AsyncMongoDB(AsyncDBStorage):
    db: AsyncIOMotorDatabase = None
    cl: AsyncIOMotorClient = None

    def __init__(self):
        self.cl: AsyncIOMotorClient | None = None

    def init_db(self, db_name):
        self.db = self.cl[db_name]

    @test_connection
    async def exec_command(self, db_name: str, command: dict, *args, **kwargs):
        res = await self.cl[db_name].command(command)
        return res

    @test_connection
    async def drop_collections(self):
        for collection in self.db.list_collection_names():
            self.db.drop_collection(collection)


mdb = AsyncMongoDB()


async def get_mongodb() -> AsyncMongoDB:
    """ Get mongodb object. """

    return mdb
