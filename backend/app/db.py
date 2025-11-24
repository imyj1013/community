users_db = []
posts_db = []
comments_db = []
likes_db = []

counters = {
    "user" : 1,
    "post" : 1,
    "comment" : 1,
    "like" : 1
}

# backend/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 예시: mysql+pymysql://user:password@localhost:3306/community?charset=utf8mb4
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/community?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    echo=True,              # SQL 로그 보고 싶으면 True
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# FastAPI DI용
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
