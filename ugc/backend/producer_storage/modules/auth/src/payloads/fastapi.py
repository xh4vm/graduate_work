from fastapi import Header
from http import HTTPStatus
from typing import Any

from modules.auth.src.exceptions.access import AccessException
from modules.auth.src.services.access.local import AccessService
from modules.auth.core.config import CONFIG as AUTH_CONFOG


class UserAccessRequired:
    def __init__(self, permissions: dict[str, list[str]]):
        self.permissions = permissions

    def __call__(self, token: str = Header(alias=AUTH_CONFOG.APP.JWT_HEADER_NAME)) -> dict[str, Any]:

        if token is not None and isinstance(token, str):
            token_parts = token.split()
            token = token_parts[1] if len(token_parts) == 2 else None

        access_service = AccessService()

        for url, method in self.permissions.items():
            response = access_service.is_accessible(token=token, method=method, url=url)

            if not response.get('is_accessible'):
                raise AccessException(status=HTTPStatus.FORBIDDEN, message=response.get('message'))

        return response['payload'].get('sub')
