from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.like_entity import Like


async def create_like(db: AsyncSession, post_id: int, user_id: int):
    like = Like(
        post_id=post_id,
        user_id=user_id,
    )
    db.add(like)
    await db.commit()
    await db.refresh(like)
    return like


async def get_like_by_id(db: AsyncSession, like_id: int):
    result = await db.execute(select(Like).where(Like.like_id == like_id))
    return result.scalars().first()


async def get_my_like(db: AsyncSession, post_id: int, session_user_id: int):
    result = await db.execute(select(Like).where(Like.post_id == post_id,Like.user_id == session_user_id))
    return result.scalars().first()


async def delete_like(db: AsyncSession, like_id: int):
    await db.execute(delete(Like).where(Like.like_id == like_id))
    await db.commit()
    return
