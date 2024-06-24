from typing import TYPE_CHECKING
from datetime import datetime
from pydantic import Field
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey
from typing import Literal

from models.base import DatabaseModel

if TYPE_CHECKING:
  from models.user import UserInDB

PublicationVisibility = Literal["all", "friends", "me"]

class PublicationInDB(DatabaseModel):
  __tablename__ = "publication"

  id: Mapped[int] = mapped_column(primary_key=True, init=False)
  content: Mapped[str]
  creation_time: Mapped[datetime] = mapped_column(default=datetime.utcnow, init=False)
  author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
  author: Mapped["UserInDB"] = relationship("UserInDB", back_populates="publications", init=False)
  visibility: Mapped[PublicationVisibility]


class CreatePublication(BaseModel):
  content: str
  visibility: PublicationVisibility = Field(default="all")


class Publication(BaseModel):
  id: int
  content: str
  creation_time: datetime
  visibility: PublicationVisibility

  model_config = ConfigDict(from_attributes=True)
