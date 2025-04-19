from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.errors import create_exception_handler
from src.auth.routes import auth_router
from src.books.routes import book_router
from src.db.main import init_db
from src.errors import (InvalidCredentialsException, InvalidTokenException, RevokedTokenException,
                        AccessTokenRequiredException, RefreshTokenRequiredException, InsufficientPermissionException,
                        UserAlreadyExistsException, UserNotFoundException, BookNotFoundException,
                        ReviewNotFoundException)
from src.reviews.routes import review_router


@asynccontextmanager
async def life_span(app: FastAPI):
    print(f'Server is starting...')

    await init_db()
    yield

    print(f'Server has been stopped')

version = 'v1'

app = FastAPI(
    title='Bookly',
    description='REST API for book webservice',
    version=version,
    lifespan=life_span,
)
app.include_router(auth_router, prefix=f'/api/{version}/auth', tags=['auth'])
app.include_router(book_router, prefix=f'/api/{version}/books', tags=['books'])
app.include_router(review_router, prefix=f'/api/{version}/reviews', tags=['reviews'])

# add exception handlers
app.add_exception_handler(
    InvalidCredentialsException, create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        init_detail={'message': 'Invalid email or password'}
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
