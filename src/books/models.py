import uuid
from datetime import datetime
from typing import Optional
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column, Relationship
from src.auth.models import User


class Book(SQLModel, table=True):
    __tablename__ = 'books'
    uid: uuid.UUID = Field(sa_column=Column(pg.UUID,
                                            nullable=False,
                                            primary_key=True,
                                            default=uuid.uuid4))
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
    create_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key='users.uid')
    # to link books to users (for user call, where we can see all books created by this user)
    user: Optional["User"] = Relationship(back_populates='books')

    def __repr__(self):
        return f'<Book {self.title}>'
