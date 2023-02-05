import json
from collections import OrderedDict
from pathlib import Path

from src.core.logger import logger
from src.core.config import SETTINGS
from src.db.mongodb import AsyncMongoDB
from src.utilities.utilities import get_data_from_json, save_data_to_file


async def perform_command_from_json_file(
        database_client: AsyncMongoDB,
        json_file_path: Path,
        save_flag: bool = False
):

    if not json_file_path.exists():
        logger.error('File {0} does not exist'.format(json_file_path))
        return False

    collections = get_data_from_json(json_file_path)

    results = {}
    for scope, collection in collections.items():
        db_name_key, collection_name, comm = scope.split('.')
        result = await database_client.exec_command(
            db_name=SETTINGS.mongo.databases[db_name_key],
            command=OrderedDict(collection)
        )
        count = result.get('n')
        if result.get('ok'):
            logger.info('Command {0} execute with ok status.{1}'.format(
                scope,
                '. Result count <{0}>.'.format(count) if count else ''
            ))
            results[scope] = result

    if save_flag:
        output_file_name = json_file_path.with_name('{0}.txt'.format(json_file_path.stem))
        save_data_to_file(output_file_name, results)
        logger.info('Results off commands save in file {0}'.format(output_file_name))
    return results
