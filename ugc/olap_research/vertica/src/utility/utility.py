from datetime import datetime
from functools import wraps

from loguru import logger


def get_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # logger.basicConfig(level=logging.DEBUG)
        start_time = datetime.now()
        result = func(*args, **kwargs)
        logger.info('Время выполнения: {0}'.format(datetime.now() - start_time))
        return result
    return wrapper
