from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.service import BookService
from src.db.main import get_session
from .schemas import Book, BookUpdateModel, BookCreateModel

book_router = APIRouter()
book_service = BookService()

@book_router.get('/', response_model=List[Book])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    books = await book_service.get_all_books(session)
    return books


@book_router.post('/', response_model=Book, status_code= status.HTTP_201_CREATED)
async def create_book(book_data: BookCreateModel, session: AsyncSession = Depends(get_session)):
    new_book = await book_service.create_book(book_data, session)
    return new_book


@book_router.get('/{book_uid}', response_model=Book)
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session)):
    book = await book_service.get_book(book_uid, session)
    if book:
        return book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')


@book_router.patch('/{book_uid}')
async def update_book(book_uid: str, update_data: BookUpdateModel,  session: AsyncSession = Depends(get_session)):
    updated_book = await book_service.update_book(book_uid, update_data, session)
    if updated_book:
        return updated_book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')


@book_router.delete('/{book_uid}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session)):
    result = await book_service.delete_book(book_uid, session)
    if result:
        return {}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')
