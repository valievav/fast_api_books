from typing import List

from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.books.service import BookService
from src.db.main import get_session
from src.errors import BookNotFoundException
from .schemas import Book, BookDetailModel, BookUpdateModel, BookCreateModel

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(['admin', 'user'])


@book_router.get('/',
                 response_model=List[Book],
                 dependencies=[Depends(access_token_bearer), Depends(role_checker)])
async def get_all_books(
        session: AsyncSession = Depends(get_session),
):
    """
    Return all books from db
    """
    books = await book_service.get_all_books(session)
    return books


@book_router.get('/user/{user_uid}',
                 response_model=List[Book],
                 dependencies=[Depends(access_token_bearer), Depends(role_checker)])
async def get_all_books_created_by_user(
        user_uid: str,
        session: AsyncSession = Depends(get_session),
):
    """
    Return all books from db that are created by specific user
    """
    books = await book_service.get_user_created_books(user_uid, session)
    return books


@book_router.post('/',
                  response_model=Book,
                  status_code= status.HTTP_201_CREATED,
                  dependencies=[Depends(role_checker)])
async def create_book(
        book_data: BookCreateModel,
        session: AsyncSession = Depends(get_session),
        token_details: dict = Depends(access_token_bearer),
):
    """
    Create new book based on provided data
    """
    user_uid = token_details['user']['user_uid']
    new_book = await book_service.create_book(book_data, user_uid, session)
    return new_book


@book_router.get('/{book_uid}',
                 response_model=BookDetailModel,
                 dependencies=[Depends(access_token_bearer), Depends(role_checker)])
async def get_book(
        book_uid: str,
        session: AsyncSession = Depends(get_session),
):
    """
    Return book based on book uid
    """
    book = await book_service.get_book(book_uid, session)
    if book:
        return book

    raise BookNotFoundException()


@book_router.patch('/{book_uid}',
                   dependencies=[Depends(access_token_bearer), Depends(role_checker)])
async def update_book(
        book_uid: str,
        update_data: BookUpdateModel,
        session: AsyncSession = Depends(get_session),
):
    """
    Update book with new data
    """
    updated_book = await book_service.update_book(book_uid, update_data, session)
    if updated_book:
        return updated_book

    raise BookNotFoundException()


@book_router.delete('/{book_uid}',
                    status_code=status.HTTP_204_NO_CONTENT,
                    dependencies=[Depends(access_token_bearer), Depends(role_checker)])
async def delete_book(
        book_uid: str,
        session: AsyncSession = Depends(get_session),
):
    """
    Delete book based on book uid
    """
    result = await book_service.delete_book(book_uid, session)
    if result:
        return {}

    raise BookNotFoundException()
