from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.user_entity import User
from sqlalchemy import select

async def create_user(db: AsyncSession, email: str, password: str, nickname: str, profile_image: str | None):
    user = User(
        email=email,
        password=password,
        nickname=nickname,
        profile_image=profile_image,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_user_by_nickname(db: AsyncSession, nickname: str):
    stmt = select(User).where(User.nickname == nickname)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int):
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def update_user_profile(db: AsyncSession, user: User, nickname: str, profile_image: str | None):
    user.nickname = nickname
    user.profile_image = profile_image
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_password(db: AsyncSession, user: User, new_password: str):
    user.password = new_password
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user_by_id(db, user_id)
    if user is None:
        return
    await db.delete(user)
    await db.commit()
