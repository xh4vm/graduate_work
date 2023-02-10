import argparse
import asyncio
from pathlib import Path

from src.core.logger import logger
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import SETTINGS
from src.db.commands.commands_utility import perform_command_from_json_file
from src.db.mongodb import mdb


class ArgumentsSetter:
    """ Class for get and set incoming arguments."""
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Created collections in the database {0}'.format(SETTINGS.mongo.databases['db_data']),
        )
        self.parser.add_argument(
            '-i',
            '--index',
            action='store_true',
            help='Create indexes. !!! Collections must be already created !!!'
        )
        self.parser.add_argument(
            '-d',
            '--drop',
            action='store_true',
            help='Drop all collections before create.'
        )
        self.arguments = self.parser.parse_args()


async def create_collections(index_flag: bool, drop_flag: bool) -> bool:
    """ Create collections

    Arguments:
        index_flag: if set only collection's indexes will be created
        drop_flag: if set  collection wil be removed before created
    Returns:
        bool: result
    """

    mdb.cl = AsyncIOMotorClient(SETTINGS.mongo.connect_string)
    mdb.init_db(SETTINGS.mongo.databases['db_data'])

    if drop_flag:
        mdb.drop_collection()
        logger.info('All collections in the database {0} have been deleted.')

    if not index_flag:
        json_schema_full_path = Path(SETTINGS.base_dir, SETTINGS.mongo.create_collections_commands_json_file)
        await perform_command_from_json_file(mdb, json_schema_full_path)

    json_schema_full_path = Path(SETTINGS.base_dir, SETTINGS.mongo.create_collections_indexes_commands_json_file)

    await perform_command_from_json_file(mdb, json_schema_full_path)


if __name__ == '__main__':
    create_indexes = ArgumentsSetter().arguments.index
    drop_collections_flag = ArgumentsSetter().arguments.drop
    asyncio.get_event_loop().run_until_complete(create_collections(create_indexes, drop_collections_flag))
    logger.info('Ok')
