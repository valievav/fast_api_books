from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config
from src.books.models import Book

engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL,
        echo=True,
    )
)

async def init_db():
    async with engine.begin() as conn:
        # statement = text("SELECT 'hello';")  # to check connection
        #
        # result = await conn.execute(statement)
        # print(result.all())

        # create tables for all SQLModels (see sql executed in server logs)
        await conn.run_sync(SQLModel.metadata.create_all)
