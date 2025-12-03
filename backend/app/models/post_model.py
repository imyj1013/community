from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.post_entity import Post
from sqlalchemy import select, delete

async def create_post(db: AsyncSession, user_id, title, content, summary, image_url, nickname):
    post = Post(
        user_id=user_id,
        title=title,
        content=content,
        summary=summary,
        image_url=image_url,
        author_nickname=nickname,
        views=0,
        comments_count=0,
        likes=0,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post

async def get_post_by_id(db: AsyncSession, post_id: int):
    result = await db.execute(select(Post).where(Post.post_id == post_id))
    return result.scalars().first()


async def get_post_list_by_id(db: AsyncSession, cursor_id: int):
    result = await db.execute(select(Post).where(Post.post_id > cursor_id).order_by(Post.post_id.asc()))
    return result.scalars().all()

async def update_post(db: AsyncSession, post, title, content, summary, image_url: str | None):
    post.title = title
    post.content = content
    post.summary = summary
    post.image_url = image_url
    await db.commit()
    await db.refresh(post)
    return post

async def delete_post(db: AsyncSession, post_id:int):
    await db.execute(delete(Post).where(Post.post_id == post_id))
    await db.commit()
    return

async def update_views(db: AsyncSession, post):
    post.views = (post.views or 0) + 1
    if post.views < 0:
        post.views = 0
    await db.commit()
    await db.refresh(post)
    return post

async def update_likes(db: AsyncSession, post, count):
    post.likes = (post.likes or 0) + count
    if post.likes < 0:
        post.likes = 0
    await db.commit()
    await db.refresh(post)
    return post

async def update_comments_count(db: AsyncSession, post, count):
    post.comments_count = (post.comments_count or 0) + count
    if post.comments_count < 0:
        post.comments_count = 0
    await db.commit()
    await db.refresh(post)
    return post