import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from app.db import Base, engine
from app.entity.user_entity import User
from app.entity.post_entity import Post
from app.entity.comment_entity import Comment
from app.entity.like_entity import Like

async def async_reset_db(async_engine: AsyncEngine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

def sync_reset_db(sync_engine):
    from sqlalchemy import inspect
    insp = inspect(sync_engine)
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)

if __name__ == "__main__":
    if isinstance(engine, AsyncEngine):
        asyncio.run(async_reset_db(engine))
    else:
        sync_reset_db(engine)