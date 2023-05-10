from typing import Optional

from fastapi import HTTPException
from fastapi.security.http import HTTPBase
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from src.auth.user_schema import HTTPAuthorizationCredentials


class HTTPBearer(HTTPBase):

    def __init__(self):
        super().__init__(scheme='bearer')

    async def __call__(self, request: Request) -> tuple[Request, Optional[HTTPAuthorizationCredentials]]:
        exc = HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail='Not authenticated',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        authorization: str = request.headers.get('Authorization')
        if authorization is None:
            raise exc
        split = authorization.split()
        if len(split) < 2:
            raise exc
        if split[0] != 'Bearer':
            raise exc
        credentials = split[-1]
        return request, HTTPAuthorizationCredentials(token=credentials)
