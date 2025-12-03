from sqlalchemy import Column, Integer, ForeignKey
from app.db import Base

class Like(Base):
    __tablename__ = "likes"

    like_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id =Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

