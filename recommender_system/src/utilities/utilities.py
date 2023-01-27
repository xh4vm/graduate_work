import json
from datetime import datetime
from functools import wraps
from uuid import UUID

import backoff
import dateutil.parser
from bson import ObjectId
from bson.errors import InvalidId
from bson.timestamp import Timestamp
from loguru import logger
from pymongo.errors import ServerSelectionTimeoutError

from src.core.config import BACKOFF_MAX_TRIES


class DateEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, Timestamp):
            return obj.as_datetime().isoformat()

        if isinstance(obj, (ObjectId, bytes)):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


def datetime_parser(json_dict):
    for (key, value) in json_dict.items():

        try:
            json_dict[key] = dateutil.parser.parse(value)
        except (ValueError, AttributeError, TypeError):
            pass

        try:
            json_dict[key] = ObjectId(value)
        except (ValueError, AttributeError, TypeError, InvalidId):
            pass

    return json_dict


def str_if_uuid(value):
    return str(value) if isinstance(value, UUID) else value


def fatal_error(err):
    logger.error('The external service for API Service ({0}) is not available now'.format(
                type(err['args'][0]).__name__
            ),
    )


def test_connection(func):
    @backoff.on_exception(
        backoff.expo,
        ServerSelectionTimeoutError,
        max_tries=BACKOFF_MAX_TRIES,
        on_giveup=fatal_error,
    )
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper
