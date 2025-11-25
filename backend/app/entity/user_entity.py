from sqlalchemy import Column, Integer, String
from app.db import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nickname = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  
    profile_image = Column(String(255))