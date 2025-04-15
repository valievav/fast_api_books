import uuid
from datetime import datetime

from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import Book
from .schemas import BookCreateModel, BookUpdateModel


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.create_date))
        result = await session.exec(statement)
        return result.all()

    async def get_user_created_books(self, user_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.create_date))
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return None or book

    async def create_book(self, book_data: BookCreateModel, user_uid: str, session: AsyncSession):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.user_uid = user_uid
        session.add(new_book)

        await session.commit()
        return new_book

    async def update_book(self, book_uid: str, upd_data: BookUpdateModel, session: AsyncSession):
        book_to_update = await self.get_book(book_uid, session)
        if not book_to_update:
            return None

        upd_data_dict = upd_data.model_dump()
        for k, v in upd_data_dict.items():
            setattr(book_to_update, k, v)  # todo - handle update_date + create_date during update

        await session.commit()
        return book_to_update

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)
        if not book_to_delete:
            return None

        await session.delete(book_to_delete)
        await session.commit()

        return True
