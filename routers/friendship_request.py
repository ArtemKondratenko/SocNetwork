from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from crud import user as user_crud
from database import get_database_session
from models.friendship_request import FriendshipRequest, FriendshipRequestInDB
from models.user import User
from security import get_current_user

friendship_request_router = APIRouter()


@friendship_request_router.post("/friendships/{receiver_nickname}")
async def create_friendship_request(
        current_user: Annotated[User, Depends(get_current_user)],
        receiver_nickname: str,
        session: Annotated[AsyncSession,
        Depends(get_database_session)],
):
    receiver = await user_crud.get_user_by_nickname(session, receiver_nickname)
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")
    friendship = FriendshipRequestInDB(sender_id=current_user.id,
                                       receiver_id=receiver.id)
    await friendship.save_in_database(session)
    return FriendshipRequest.model_validate(friendship)


@friendship_request_router.get("/friendships/requests")
async def get_friendship_requests(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_database_session)],
):
    friendship_requests = await user_crud.get_friendship_requests(session, current_user)
    friendship_requests = [FriendshipRequest.model_validate(request) for request in friendship_requests]
    return friendship_requests


@friendship_request_router.post("/friendships/decline/{sender_nickname}")
async def decline_friendship_request(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_database_session)],
        sender_nickname: str,
):
    sender = await user_crud.get_user_by_nickname(session, sender_nickname)
    if not sender:
        raise HTTPException(status_code=404, detail="User not found")
    sender = User.model_validate(sender)
    friendship_request = await user_crud.decline_friendship_request(session, sender, current_user)
    return FriendshipRequest.model_validate(friendship_request)


@friendship_request_router.post("/friendships/confirm/{sender_nickname}")
async def confirm_friendship_request(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_database_session)],
        sender_nickname: str,
):
    sender = await user_crud.get_user_by_nickname(session, sender_nickname)
    if not sender:
        raise HTTPException(status_code=404, detail="User not found")
    sender = User.model_validate(sender)
    sender_result = await user_crud.confirm_friendship_request(session, sender, current_user)
    return User.model_validate(sender_result)


@friendship_request_router.post("/friends/{user_nickname}")
async def view_list_friends(
        session: Annotated[AsyncSession, Depends(get_database_session)],
        user_nickname: str
):
    user = await user_crud.get_user_by_nickname(session, user_nickname)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return [User.model_validate(friend) for friend in (await user.awaitable_attrs.friends)]


@friendship_request_router.delete("/delete/friend/{friend_nickname}")
async def delete_friend(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_database_session)],
        friend_nickname: str
):
    remove_friend = await user_crud.get_user_by_nickname(session, friend_nickname)
    if not remove_friend:
        raise HTTPException(status_code=404, detail="User not found")
    user = await user_crud.delete_friend_request(session, current_user, remove_friend)
    return User.model_validate(user)


@friendship_request_router.get("/friendships/potential_friends")
async def potential_friends(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_database_session)]
):
    friends = await user_crud.potential_friends(session, current_user)
    return [User.model_validate(friend) for friend in friends]
