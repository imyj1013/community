from app import db
from sqlalchemy.orm import Session
from app.entity.post_entity import Post

def create_post(db: Session, user_id, title, content, summary, image_url, nickname):
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
    db.commit()
    db.refresh(post)
    return post

def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.post_id == post_id).first()

def get_post_list_by_id(db: Session, cursor_id: int):
    return (
        db.query(Post)
        .filter(Post.post_id > cursor_id)
        .order_by(Post.post_id.asc())
        .all()
    )

def update_post(db: Session, post, title, content, summary, image_url):
    post.title = title
    post.content = content
    post.summary = summary
    post.image_url = image_url
    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post_id:int):
    db.query(Post).filter(Post.post_id == post_id).delete(synchronize_session=False)
    db.commit()
    return

def update_likes(db: Session, post, count):
    post.likes = (post.likes or 0) + count
    if post.likes < 0:
        post.likes = 0
    db.commit()
    db.refresh(post)
    return post

def update_comments_count(db: Session, post, count):
    post.comments_count = (post.comments_count or 0) + count
    if post.comments_count < 0:
        post.comments_count = 0
    db.commit()
    db.refresh(post)
    return post