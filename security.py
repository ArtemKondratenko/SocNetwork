from settings import SECRET_KEY
from jose import jwt
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing_extensions import Annotated
from fastapi import Depends,status
from sqlalchemy.ext.asyncio.session import AsyncSession
from database import get_database_session
from models.user import User
from crud.user import get_user_by_nickname
from database import get_database_session
from models.user import User
from settings import SECRET_KEY


def check_password(password: str) -> bool:
    return True

def create_token(data: dict) -> str:
  return jwt.encode(data, SECRET_KEY)

get_auth_token = OAuth2PasswordBearer(tokenUrl="login")
get_auth_token_or_none = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

async def get_current_user(
    token: Annotated[str, Depends(get_auth_token)],
    session: Annotated[AsyncSession,
                       Depends(get_database_session)],
) -> User:
  data = jwt.decode(token, SECRET_KEY)
  nickname = data["nickname"]
  userInDB = await get_user_by_nickname(session, nickname)
  if not userInDB:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
  return User.model_validate(userInDB)


async def get_current_user_or_none(
  token: Annotated[str | None, Depends(get_auth_token_or_none)],
  session: Annotated[AsyncSession,
                     Depends(get_database_session)],
) -> User | None:
  if not token:
    return None
  try:
    data = jwt.decode(token, SECRET_KEY)
    nickname = data["nickname"]
    userInDB = await get_user_by_nickname(session, nickname)
    if not userInDB:
      return None
    return User.model_validate(userInDB)
  except Exception:
    return None
