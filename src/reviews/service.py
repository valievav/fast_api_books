from http.client import HTTPException

from fastapi import HTTPException, status
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review
from .schemas import ReviewCreateModel

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.create_date))
        result = await session.exec(statement)
        return result.all()

    async def get_user_created_reviews(self, user_uid: str, session: AsyncSession):
        statement = select(Review).where(Review.user_uid == user_uid).order_by(desc(Review.create_date))
        result = await session.exec(statement)
        return result.all()

    async def get_review(self, review_uid: str, session: AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)
        result = await session.exec(statement)
        review = result.first()
        return None or review

    async def add_review(self, user_email: str, book_uid: str,
                         review_data: ReviewCreateModel, session: AsyncSession):
        book = await book_service.get_book(book_uid, session)
        user = await user_service.get_user_by_email(user_email, session)

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Book not found'
            )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        review_data_dict = review_data.model_dump()
        review = Review(**review_data_dict)
        review.user = user
        review.book = book

        session.add(review)
        await session.commit()
        return review
