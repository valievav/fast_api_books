import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Review(BaseModel):
    uid: uuid.UUID
    rating: int
    review_text: str
    user_uid: Optional[uuid.UUID]
    book_uid: Optional[uuid.UUID]
    create_date: datetime
    update_date: datetime


class ReviewCreateModel(BaseModel):
    rating: int
    review_text: str
