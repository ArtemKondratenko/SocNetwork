from __future__ import annotations

from pydantic.main import BaseModel, ConfigDict
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import DatabaseModel
from models.user import UserInDB


class FriendshipRequestInDB(DatabaseModel):
    __tablename__ = "friendship_request"

    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    sender: Mapped[UserInDB] = relationship(foreign_keys=[sender_id], init=False)
    receiver: Mapped[UserInDB] = relationship(foreign_keys=[receiver_id], init=False)

    is_declined: Mapped[bool] = mapped_column(default=False, init=False)


class FriendshipRequest(BaseModel):
    sender_id: int
    receiver_id: int
    is_declined: bool

    model_config = ConfigDict(from_attributes=True)

