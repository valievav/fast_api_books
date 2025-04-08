import uuid
from datetime import datetime

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column


class Book(SQLModel, table=True):
    __tablename__ = 'books'
    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False,
                                            primary_key=True, default=uuid.uuid4))
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
    create_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f'<Book {self.title}>'
