from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.publication import PublicationInDB
from models.user import User, UserInDB
from crud.user import get_user_by_nickname


async def get_publications(
    session: AsyncSession,
    nickname: str | None = None) -> Iterable[PublicationInDB]:
  stmt = select(PublicationInDB)
  if nickname is not None:
    stmt = stmt.join(
        PublicationInDB.author).where(UserInDB.nickname == nickname)
  return (await session.scalars(stmt)).all()


async def get_publication(session: AsyncSession, publication_id: int):
  stmt = select(PublicationInDB).where(PublicationInDB.id == publication_id)
  return (await session.scalars(stmt)).one()


async def delete_publication(session: AsyncSession,
                             publication: PublicationInDB):
  await session.delete(publication)


async def is_visible_by(
    _session: AsyncSession,
    publication: PublicationInDB,
    user: UserInDB | None,
) -> bool:
  author = await publication.awaitable_attrs.author

  if publication.visibility == "me":
    return user == author

  if publication.visibility == "friends":
    return user in await author.awaitable_attrs.friends or user == author

  if publication.visibility == "all":
    return True

  return False



# Model.attribute = relationship
# (await Model.awaitable_attrs.attribute)

# publication.visiiblity = "all" | "friends" | "me"
