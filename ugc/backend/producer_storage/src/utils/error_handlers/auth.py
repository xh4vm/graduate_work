from fastapi import HTTPException
from http import HTTPStatus
from modules.auth.src.exceptions.access import AccessException

from src.core.config import service_logger


async def error_handler() -> None:
    try:
        yield
    except AccessException as access_exception:
        raise HTTPException(status_code=access_exception.status, detail=access_exception.message)
    except Exception as exception:
        service_logger.error(exception, exc_info=True)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='')
