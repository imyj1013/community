from app.entity.user_entity import User
from app.entity.post_entity import Post
from app.entity.like_entity import Like
from app.entity.comment_entity import Comment
from app.db import Base, engine

Base.metadata.create_all(bind=engine)