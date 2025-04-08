from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import create_engine, SQLModel

from src.config import Config

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
