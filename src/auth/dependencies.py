from typing import List, Optional

from fastapi import Request, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User
from src.db.redis import token_in_blocklist
from src.errors import (AccessTokenRequiredException, InvalidTokenException, RevokedTokenException,
                        RefreshTokenRequiredException, InsufficientPermissionException)
from .service import UserService
from .utils import decode_access_token

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __int__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = decode_access_token(token)

        if not self.token_valid(token):
            raise InvalidTokenException()

        if await token_in_blocklist(token_data['jti']):
            raise RevokedTokenException()

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_access_token(token)
        return bool(token_data)

    def verify_token_data(self, token_data: dict):
        raise NotImplementedError('Please override this method in child classes')


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data['refresh']:
            raise AccessTokenRequiredException()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data['refresh']:
            raise RefreshTokenRequiredException()


async def get_current_user(token_details: dict = Depends(AccessTokenBearer()),
                           session: AsyncSession = Depends(get_session)):
    user_email = token_details['user']['email']
    user = await user_service.get_user_by_email(user_email, session)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: Optional[List[str]] = None) -> None:
        self.allowed_roles = allowed_roles or ['admin',]

    def __call__(self, current_user: User = Depends(get_current_user)) -> bool:
        if current_user.role not in self.allowed_roles:
            raise InsufficientPermissionException()
        return True
