from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from database import get_database_session
from models.user import CreateUser, User, UserInDB
from security import check_password, get_current_user

user_router = APIRouter()


@user_router.get("/users/{user_id}")
async def get_user_by_id(user_id: int,
                         session: Annotated[AsyncSession,
                         Depends(get_database_session)],) -> User:
  userInDB = await session.get(UserInDB, user_id)
  if not userInDB:
    raise HTTPException(status_code=404, detail="User not found")
  return User.model_validate(userInDB)


@user_router.post("/users")
async def create_user(
    user_data: CreateUser,
    session: Annotated[AsyncSession,
                       Depends(get_database_session)],
) -> User:
    if not check_password(user_data.password):
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    userInDB = UserInDB(nickname=user_data.nickname, password=user_data.password)
    await userInDB.save_in_database(session)
    return User.model_validate(userInDB)


@user_router.get("/whoami")
async def who_am_i(current_user: Annotated[User, Depends(get_current_user)]) -> User:
  return current_user
