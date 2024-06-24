from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
  AsyncSession,
  async_sessionmaker,
  create_async_engine,
)

from models.base import DatabaseModel
from settings import DATABASE_URL

_engine = create_async_engine(DATABASE_URL, echo=True)
_async_session = async_sessionmaker(_engine)

async def init_database():
  async with _engine.begin() as conn:
    await conn.run_sync(DatabaseModel.metadata.create_all)


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
  async with _async_session() as session:
    yield session
    await session.commit()