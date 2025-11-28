from app import db
from sqlalchemy.orm import Session
from app.entity.user_entity import User
from .. import utils

def create_user(db: Session, email: str, password: str, nickname: str, profile_image: str | None):
    hashed_pwd = utils.hash_password(password)
    user = User(
        email=email,
        password=hashed_pwd,
        nickname=nickname,
        profile_image=profile_image,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    return db.query(User).filter(User.email == email).first()

def get_user_by_nickname(db: Session, nickname: str):
    return db.query(User).filter(User.nickname == nickname).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()

def update_user_profile(db: Session, user: User, nickname: str, profile_image: str | None):
    user.nickname = nickname
    if profile_image is not None:
        user.profile_image = profile_image
    db.commit()
    db.refresh(user)
    return user

def update_user_password(db: Session, user: User, new_password: str):
    user.password = new_password
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if user is None:
        return
    db.delete(user)
    db.commit()
