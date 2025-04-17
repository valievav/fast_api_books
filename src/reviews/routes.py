from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import get_current_user
from src.db.main import get_session
from src.db.models import User
from .schemas import ReviewCreateModel
from .service import ReviewService

review_router = APIRouter()
review_service = ReviewService()


@review_router.post('/book/{book_uid}')
async def add_review_to_book(book_uid: str,
                             review_data: ReviewCreateModel,
                             user: User = Depends(get_current_user),
                             session: AsyncSession = Depends(get_session)):
    review = await review_service.add_review(user.email, book_uid, review_data, session)
    return review
