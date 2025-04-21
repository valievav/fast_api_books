from typing import Any

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class BooklyException(Exception):
    """
    Base class for all app exceptions
    """
    pass


class InvalidCredentialsException(BooklyException):
    pass


class AccountNotVerifiedException(BooklyException):
    pass


class InvalidTokenException(BooklyException):
    pass


class RevokedTokenException(BooklyException):
    pass


class PasswordsDoNotMatchException(BooklyException):
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

    async def exception_handler(request: Request, exc: Exception):
        return JSONResponse(content=init_detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        InvalidCredentialsException, create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            init_detail={'message': 'Invalid email or password'}
        )
    )
    app.add_exception_handler(
        AccountNotVerifiedException, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            init_detail={'message': 'Account is not verified yet',
                         'resolution': 'Please check your email for verification link'}
        )
    )
    app.add_exception_handler(
        InvalidTokenException, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            init_detail={'message': 'This token is invalid or expired'}
        )
    )
    app.add_exception_handler(
        RevokedTokenException, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            init_detail={'message': 'This token is invalid or revoked'}
        )
    )
    app.add_exception_handler(
        PasswordsDoNotMatchException, create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            init_detail={'message': 'Passwords do not match'}
        )
    )
    app.add_exception_handler(
        AccessTokenRequiredException, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            init_detail={'message': 'Please provide an access token'}
        )
    )
    app.add_exception_handler(
        RefreshTokenRequiredException, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            init_detail={'message': 'Please provide a refresh token'}
        )
    )
    app.add_exception_handler(
        InsufficientPermissionException, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            init_detail={'message': 'User has no permission to perform the action'}
        )
    )
    app.add_exception_handler(
        UserAlreadyExistsException, create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            init_detail={'message': 'User already exists'}
        )
    )
    app.add_exception_handler(
        UserNotFoundException, create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            init_detail={'message': 'User not found'}
        )
    )
    app.add_exception_handler(
        BookNotFoundException, create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            init_detail={'message': 'Book not found'}
        )
    )
    app.add_exception_handler(
        ReviewNotFoundException, create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            init_detail={'message': 'Review not found'}
        )
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exception):
        return JSONResponse(content={'message': 'Something went wrong'},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

