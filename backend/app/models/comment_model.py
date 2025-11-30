from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.comment_entity import Comment


async def create_comment(db: AsyncSession, post_id: int, user_id: int, content: str):
    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comment_by_id(db: AsyncSession, comment_id: int):
    result = await db.execute(select(Comment).where(Comment.comment_id == comment_id))
    return result.scalars().first()


async def update_comment(db: AsyncSession, comment: Comment, content: str):
    comment.content = content
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(db: AsyncSession, comment_id: int):
    await db.execute(delete(Comment).where(Comment.comment_id == comment_id))
    await db.commit()
    return


async def get_comment_by_post_id(db: AsyncSession, post_id: int):
    result = await db.execute(select(Comment).where(Comment.post_id == post_id).order_by(Comment.comment_id.asc()))
    return result.scalars().all()
