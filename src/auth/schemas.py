import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from src.books.schemas import Book


class User(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)  # field will be hidden, not be serialized
    create_date: datetime
    update_date: datetime


class UserBooks(User):
    books: List[Book]  # return list of books created by user


class UserCreateModel(BaseModel):
    username: str = Field(max_length=25)
    email: str = Field(max_length=40)
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    password: str = Field(min_length=5)


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=5)


class EmailModel(BaseModel):
    addresses: list[str]
