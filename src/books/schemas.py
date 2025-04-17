import uuid
from datetime import datetime
from typing import List
from src.reviews.schemas import Review
from pydantic import BaseModel


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
    create_date: datetime
    update_date: datetime


class BookDetailModel(Book):
    reviews: List[Review]


class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
