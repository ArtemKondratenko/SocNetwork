from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import get_user_by_nickname
from database import get_database_session
from models.auth import Token
from security import create_token

auth_router = APIRouter()


@auth_router.post("/login")
async def login(
    user_data: Annotated[OAuth2PasswordRequestForm,
                         Depends()],
    session: Annotated[AsyncSession,
                       Depends(get_database_session)]) -> Token:
  nickname = user_data.username
  password = user_data.password

  user = await get_user_by_nickname(session, nickname)

  if (not user) or (user and user.password != password):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

  return Token(access_token=create_token({"nickname": nickname}), token_type="bearer")
