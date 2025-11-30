from app.entity.user_entity import User
from app.entity.post_entity import Post
from app.entity.like_entity import Like
from app.entity.comment_entity import Comment
from app.db import Base, engine
import asyncio

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())