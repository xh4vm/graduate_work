import json
from collections import OrderedDict
from pathlib import Path

from loguru import logger
from src.core.config import MONGO_DATABASES
from src.db.receiver.mongodb.mongodb import AsyncMongoDB
from src.utilities.utilities import DateEncoder, datetime_parser


async def perform_command_from_json_file(
        database_client: AsyncMongoDB,
        json_file_path: Path,
        save_flag: bool = False
):

    if not json_file_path.exists():
        logger.error('File {0} does not exist'.format(json_file_path))
        return False

    with open(json_file_path, 'r') as input_file:
        collections = json.loads(input_file.read(), object_hook=datetime_parser)

    results = {}
    for scope, collection in collections.items():
        db_name_key, collection_name, comm = scope.split('.')
        result = await database_client.exec_command(
            db_name=MONGO_DATABASES[db_name_key],
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
        with open(output_file_name, 'w') as output_file:
            json.dump(results, output_file, cls=DateEncoder)
        logger.info('Results off commands save in file {0}'.format(output_file_name))
    return results
