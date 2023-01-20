from functools import wraps
from http import HTTPStatus
from typing import Optional

import modules.auth.src.services.access.grpc as grpc_client_connector
import backoff
import grpc
from modules.auth.core.config import BACKOFF_CONFIG, CONFIG, auth_logger
from modules.auth.src.exceptions.access import AccessException
from modules.auth.src.services.access.local import AccessService
from grpc import aio


def access_required(permissions: dict[str, str], token_name: str = 'x_authorization_token'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = kwargs.get(token_name)

            if token is not None and isinstance(token, str):
                token = token.split()[1]

            access_service = AccessService()

            for url, method in permissions.items():
                response = access_service.is_accessible(token=token, method=method, url=url)

                if not response.get('is_accessible'):
                    raise AccessException(status=HTTPStatus.FORBIDDEN, message=response.get('message'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def async_grpc_access_required(permissions: dict[str, str]):
    def decorator(f):
        @backoff.on_exception(**BACKOFF_CONFIG, exception=grpc.RpcError, logger=auth_logger)
        @wraps(f)
        async def decorated_function(token: Optional[str], *args, **kwargs):
            async with aio.insecure_channel(target=f'{CONFIG.GRPC.HOST}:{CONFIG.GRPC.PORT}') as channel:

                access_service = grpc_client_connector.AsyncAccessService(channel)

                for url, method in permissions.items():

                    response = await access_service.is_accessible(token=token, method=method, url=url)

                    if not response.get('is_accessible'):
                        raise AccessException(status=HTTPStatus.FORBIDDEN, message=response.get('message'))

            return await f(*args, **kwargs)

        return decorated_function

    return decorator


def grpc_access_required(permissions: dict[str, str]):
    def decorator(f):
        @backoff.on_exception(**BACKOFF_CONFIG, exception=grpc.RpcError, logger=auth_logger)
        @wraps(f)
        def decorated_function(token: Optional[str], *args, **kwargs):
            with grpc.insecure_channel(target=f'{CONFIG.GRPC.HOST}:{CONFIG.GRPC.PORT}') as channel:

                access_service = grpc_client_connector.AccessService(channel)

                for url, method in permissions.items():
                    response = access_service.is_accessible(token=token, method=method, url=url)

                    if not response.get('is_accessible'):
                        raise AccessException(status=HTTPStatus.FORBIDDEN, message=response.get('message'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator
