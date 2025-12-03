from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from app.db import Base

class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)
    author_nickname = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    views = Column(Integer, nullable=False, server_default="0")
    comments_count = Column(Integer, nullable=False, server_default="0")
    likes = Column(Integer, nullable=False, server_default="0")