from sqlalchemy.orm import Session
from app.entity.like_entity import Like

def create_like(db: Session, post_id:int, user_id:int):
    like = Like(
        post_id=post_id,
        user_id=user_id,
    )
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


def get_like_by_id(db: Session, like_id: int):
    return db.query(Like).filter(Like.like_id == like_id).first()

def get_my_like(db: Session, post_id, session_user_id):
    return (
        db.query(Like)
        .filter(Like.post_id == post_id, Like.user_id == session_user_id)
        .first()
    )

def delete_like(db: Session, like_id: int):
    db.query(Like).filter(Like.like_id == like_id).delete(synchronize_session=False)
    db.commit()
    return
