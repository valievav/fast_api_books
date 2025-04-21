from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.db.main import init_db
from src.errors import register_all_errors
from src.middleware import register_middleware
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
register_all_errors(app)
register_middleware(app)

app.include_router(auth_router, prefix=f'/api/{version}/auth', tags=['auth'])
app.include_router(book_router, prefix=f'/api/{version}/books', tags=['books'])
app.include_router(review_router, prefix=f'/api/{version}/reviews', tags=['reviews'])
