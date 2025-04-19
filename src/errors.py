from typing import Any

from fastapi.requests import Request
from fastapi.responses import JSONResponse


class BooklyException(Exception):
    """
    Base class for all app exceptions
    """
    pass


class InvalidCredentialsException(BooklyException):
    pass


class InvalidTokenException(BooklyException):
    pass


class RevokedTokenException(BooklyException):
    pass


class AccessTokenRequiredException(BooklyException):
    pass


class RefreshTokenRequiredException(BooklyException):
    pass


class InsufficientPermissionException(BooklyException):
    pass


class UserAlreadyExistsException(BooklyException):
    pass


class UserNotFoundException(BooklyException):
    pass


class BookNotFoundException(BooklyException):
    pass


class ReviewNotFoundException(BooklyException):
    pass


def create_exception_handler(status_code: int, init_detail: Any):

    async def exception_handler(request: Request, exc: BooklyException):
        return JSONResponse(content=init_detail, status_code=status_code)

    return exception_handler
