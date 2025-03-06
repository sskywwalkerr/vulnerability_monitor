import uuid
from datetime import datetime
from typing import Any, List
from fastapi import Depends, Request

from api.dao.users_dao import UsersDAO
from jose import JWTError, jwt
from sqlalchemy import Row, RowMapping

from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from api.auth.service import UserService, AdminService
from api.auth.utils import decode_token
from api.config import Config
from api.errors import (
    InvalidToken,
    AccessTokenRequired,
    RefreshTokenRequired,
    AccountNotVerified,
    InsufficientPermission, IncorrectTokenFormatException, TokenExpiredException, UserDoesNotExistException,
    TokenAbsentException,
)
from api.models.User import User

from api.db.redis import token_in_blocklist
from api.db.data import get_session

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()

        if await token_in_blocklist(token_data["jti"]):
            raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)

        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Пожалуйста, переопределите этот метод в дочерних классах")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]

    user = await user_service.get_user_by_email(user_email, session)

    return user


def get_token(request: Request) -> str:
    """Получение токена доступа из куки запроса"""

    token = request.cookies.get('access_token')
    if not token:
        raise TokenAbsentException()
    return token


# async def get_current_users(token: str = Depends(get_token)) -> Row:
#     """Декодирование jwt и получение user по его uid из токена"""
#
#     try:
#         payload = jwt.decode(
#             token, Config.JWT_SECRET, Config.JWT_ALGORITHM
#         )
#     except JWTError:
#         raise IncorrectTokenFormatException()
#
#     expire = payload.get('exp')
#     if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
#         raise TokenExpiredException()
#
#     user_uid = payload.get('sub')
#     if not user_uid:
#         raise IncorrectTokenFormatException()
#
#     user = await AdminService.get_by_uid(uid=uuid.UUID(user_uid))
#     if not user:
#         raise UserDoesNotExistException()
#
#     return user
async def get_current_users(token: str = Depends(get_token)) -> RowMapping:
    """Получает JWT-токен. Декодирует токен в полезную нагрузку (dict) и проверяет ее.
    Далее, если в ней есть subject (id), ищет его в БД. Если такой есть, возвращает юзера.
    """
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, Config.JWT_ALGORITHM)
    except JWTError:
        raise IncorrectTokenFormatException()

    user_uid: str | None = payload.get("sub")
    if not user_uid:
        raise IncorrectTokenFormatException()

    user = await UsersDAO.find_one_or_none(uid=uuid.UUID(user_uid))
    if not user:
        raise UserDoesNotExistException()
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
