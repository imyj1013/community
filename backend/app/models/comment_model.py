from app import db
from sqlalchemy.orm import Session
from app.entity.comment_entity import Comment

def create_comment(db: Session, post_id, user_id, content):
    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def get_comment_by_id(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.comment_id == comment_id).first()

def update_comment(db: Session, comment, content):
    comment.content = content
    db.commit()
    db.refresh(comment)
    return comment

def delete_comment(db: Session, comment_id):
    db.query(Comment).filter(Comment.comment_id == comment_id).delete(
        synchronize_session=False
    )
    db.commit()
    return

def get_comment_by_post_id(db: Session, post_id:int):
    return (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.comment_id.asc())
        .all()
    )
