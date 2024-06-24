
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from crud import publication as publication_crud
from database import get_database_session
from models.publication import CreatePublication, Publication, PublicationInDB
from models.user import User
from security import get_current_user, get_current_user_or_none
from crud.user import get_user_by_nickname

publication_router = APIRouter()


@publication_router.post("/publications")
async def create_publication(
    publication_data: CreatePublication,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession,
                       Depends(get_database_session)],
) -> Publication:
  publicationInDB = PublicationInDB(content=publication_data.content,
                                    author_id=current_user.id, visibility=publication_data.visibility,)
  await publicationInDB.save_in_database(session)
  return Publication.model_validate(publicationInDB)




@publication_router.get("/publications/")
async def get_publications(
  current_user: Annotated[User | None, Depends(get_current_user_or_none)],
  session: Annotated[AsyncSession,
                           Depends(get_database_session)],
                          nickname: str | None = None) -> list[Publication]:
  publications = await publication_crud.get_publications(session, nickname)
  user = None
  if current_user:
    user = await get_user_by_nickname(session, current_user.nickname)
  else:
    user = None
  return [Publication.model_validate(publication) for publication in publications if await publication_crud.is_visible_by(session, publication, user)]


@publication_router.delete("/publications/")
async def delete_publication(
  current_user: Annotated[User, Depends(get_current_user)],
  session: Annotated[AsyncSession, Depends(get_database_session)],
  publication_id: int):
  publication = await publication_crud.get_publication(session, publication_id)
  if not publication or (await publication.awaitable_attrs.author).nickname != current_user.nickname:
    raise HTTPException(status_code=404, detail="There is no publication or there are no rights to delete")
  await publication_crud.delete_publication(session, publication)
  return Publication.model_validate(publication)
