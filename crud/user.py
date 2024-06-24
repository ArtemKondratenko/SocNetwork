from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.friendship_request import FriendshipRequestInDB
from models.user import User, UserInDB


async def get_user_by_nickname(session: AsyncSession, nickname: str) -> UserInDB | None:
    stmt = select(UserInDB).where(UserInDB.nickname == nickname)
    return (await session.scalars(stmt)).first()


async def get_friendship_requests(session: AsyncSession, user: User) -> List[FriendshipRequestInDB]:
    stmt = select(FriendshipRequestInDB).where(FriendshipRequestInDB.receiver_id == user.id)
    result = await session.execute(stmt)
    friendship_requests = result.scalars().all()
    return list(friendship_requests)


async def decline_friendship_request(session: AsyncSession, sender: User,
                                     receiver: User) -> FriendshipRequestInDB | None:
    friendship_request = await session.get(FriendshipRequestInDB, (sender.id, receiver.id))
    # stmt = select(FriendshipRequestInDB).where(FriendshipRequestInDB.sender_id==sender.id, FriendshipRequestInDB.receiver_id==receiver.id)

    # friendship_request = (await session.scalars(stmt)).first()
    # print(friendship_request)

    if not friendship_request:
        return None
    friendship_request.is_declined = True
    await session.delete(friendship_request)
    return friendship_request


async def confirm_friendship_request(session: AsyncSession, sender: User, receiver: User) -> UserInDB | None:
    friendship_request = await session.get(FriendshipRequestInDB, (sender.id, receiver.id))

    if not friendship_request:
        return None

    user_sender_result = await get_user_by_nickname(session, sender.nickname)
    user_receiver_result = await get_user_by_nickname(session, receiver.nickname)

    if user_sender_result is None or user_receiver_result is None:
        return None
    friends = await user_sender_result.awaitable_attrs.friends
    friends.append(user_receiver_result)

    friends = await user_receiver_result.awaitable_attrs.friends
    friends.append(user_sender_result)
    # user_receiver_result.list_friends.append(user_sender_result.nickname)
    await session.delete(friendship_request)
    return user_sender_result


async def delete_friend_request(session: AsyncSession, current_user: User, remove_friend: UserInDB) -> UserInDB | None:
    user = await get_user_by_nickname(session, current_user.nickname)
    friend = await get_user_by_nickname(session, remove_friend.nickname)
    if not user or not friend:
        return None
    (await user.awaitable_attrs.friends).remove(friend)
    (await friend.awaitable_attrs.friends).remove(user)
    return user


async def potential_friends(
        session: AsyncSession,
        current_user: User
) -> list[UserInDB]:
    user = await get_user_by_nickname(session, current_user.nickname)
    if not user:
        return []

    friends: list[UserInDB] = await user.awaitable_attrs.friends
    friends_friends = []
    for friend in friends:
        humans = await friend.awaitable_attrs.friends
        for human in humans:
            if human.nickname != user.nickname:
                friends_friends.append(human)

    unique_friends_friends = list(set(friends_friends))
    return unique_friends_friends

