import uuid
from datetime import datetime
from typing import List

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column, Relationship

from src.books.schemas import Book


class User(SQLModel, table=True):
    __tablename__ = 'users'
    uid: uuid.UUID = Field(sa_column=Column(pg.UUID,
                                            nullable=False,
                                            primary_key=True,
                                            default=uuid.uuid4))
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default='user'))
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)  # to hide field from response
    create_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    # to link to books, to be able to return all books created by the current user
    books: List['Book'] = Relationship(back_populates='user', sa_relationship_kwargs={'lazy': 'selectin'})

    def __repr__(self):
        return f'<User {self.username}>'
