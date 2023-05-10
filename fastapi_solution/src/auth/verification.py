from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from starlette.status import HTTP_403_FORBIDDEN

from src.auth.bearer import HTTPBearer
from src.auth.user_schema import User, HTTPAuthorizationCredentials
from src.core.config import settings

security = HTTPBearer()


def decode_token(token: str) -> User:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str('Could not validate credentials'),
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return User.parse_obj(payload)


def get_user(request: Request) -> User:
    return request.state.user


class Access:
    def __init__(self, roles: set[str]):
        self.roles = roles

    def __call__(self, request_user: tuple[Request, HTTPAuthorizationCredentials] = Depends(security)) -> None:
        exc = HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail='Not authenticated',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        request, user = request_user
        user = decode_token(user.token)
        if self.roles not in user.roles and user.is_admin is False:
            raise exc
        request.state.user = user
