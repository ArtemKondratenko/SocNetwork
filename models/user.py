
from __future__ import annotations
from sqlalchemy import Column, Table
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import or_
from models.base import DatabaseModel
from models.publication import PublicationInDB

# many-to-many

friendship_association_table = Table(
    "friendship_association_table",
    DatabaseModel.metadata,
    Column("user1_id", ForeignKey("user.id")),
    Column("user2_id", ForeignKey("user.id")),
)


class UserInDB(DatabaseModel):
  __tablename__ = "user"

  id: Mapped[int] = mapped_column(
      primary_key=True,
      autoincrement=True,
      init=False,
  )
  nickname: Mapped[str] = mapped_column(unique=True)
  password: Mapped[str]
  friends: Mapped[list["UserInDB"]] = relationship(
      secondary=friendship_association_table,
      primaryjoin=(friendship_association_table.c.user1_id == id),
      secondaryjoin=(friendship_association_table.c.user2_id == id),
      init=False,
      repr=False,
  )
  publications: Mapped[list["PublicationInDB"]] = relationship(
      "PublicationInDB",
      back_populates='author',
      init=False,
  )

  def __eq__(self, other: object) -> bool:
    if not isinstance(other, UserInDB):
      return False
    return self.id == other.id

  def __hash__(self):
    return hash(self.id)


class CreateUser(BaseModel):
  nickname: str
  password: str


class User(BaseModel):
  id: int
  nickname: str

  model_config = ConfigDict(from_attributes=True)
