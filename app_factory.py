from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_database
from routers.auth import auth_router
from routers.friendship_request import friendship_request_router
from routers.user import user_router
from routers.publication import publication_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
  print("App is started")
  await init_database()
  yield
  print("App is closed")


def create_app() -> FastAPI:
  app = FastAPI(lifespan=lifespan)
  app.include_router(auth_router)
  app.include_router(user_router)
  app.include_router(friendship_request_router)
  app.include_router(publication_router)
  return app
