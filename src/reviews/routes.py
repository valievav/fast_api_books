from typing import List

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.auth.dependencies import get_current_user
from src.db.main import get_session
from src.db.models import User
from src.errors import ReviewNotFoundException
from .schemas import Review, ReviewCreateModel
from .service import ReviewService

review_router = APIRouter()
review_service = ReviewService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(['admin', 'user'])


@review_router.get('/',
                   response_model=List[Review],
                   dependencies=[Depends(access_token_bearer), Depends(role_checker)])
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    """
    Return all reviews
    """
    reviews = await review_service.get_all_reviews(session)
    return reviews


@review_router.get('/user/{user_uid}', response_model=List[Review],
                 dependencies=[Depends(access_token_bearer), Depends(role_checker)])
async def get_all_reviews_created_by_user(
        user_uid: str,
        session: AsyncSession = Depends(get_session),
):
    """
    Return all reviews from db that are created by specific user
    """
    reviews = await review_service.get_user_created_reviews(user_uid, session)
    return reviews


@review_router.post('/book/{book_uid}')
async def add_review_to_book(book_uid: str,
                             review_data: ReviewCreateModel,
                             user: User = Depends(get_current_user),
                             session: AsyncSession = Depends(get_session)):
    """
    Add review to a book
    """
    review = await review_service.add_review(user.email, book_uid, review_data, session)
    return review


@review_router.get('/{review_uid}',
                 response_model=Review,
                 dependencies=[Depends(access_token_bearer), Depends(role_checker)])
async def get_review(
        review_uid: str,
        session: AsyncSession = Depends(get_session),
):
    """
    Return review based on review uid
    """
    review = await review_service.get_review(review_uid, session)
    if review:
        return review

    raise ReviewNotFoundException()
