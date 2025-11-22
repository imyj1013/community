import re
from . import db

def find_user_by_email(email: str):
    return next((u for u in db.users_db if u["email"] == email), None)

def find_user_by_nickname(nickname: str):
    return next((u for u in db.users_db if u["nickname"] == nickname), None)

def find_user_by_id(user_id: int):
    return next((u for u in db.users_db if u["user_id"] == user_id), None)

def find_post_by_id(post_id: int):
    return next((p for p in db.posts_db if p["post_id"] == post_id), None)

def find_comment_by_id(comment_id: int):
    return next((c for c in db.comments_db if c["comment_id"] == comment_id), None)

def find_like_by_id(like_id: int):
    return next((l for l in db.likes_db if l["like_id"] == like_id), None)

def email_is_valid(email: str):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def nickname_is_valid(nickname: str):
    pattern = r'^\S{1,10}$'
    return re.match(pattern, nickname) is not None

def format_number(n: int) -> str:
    if n >= 100_000:
        return f"{n // 1000}k"
    elif n >= 10_000:
        return f"{n // 1000}k"
    elif n >= 1_000:
        return f"{n // 1000}k"
    else:
        return str(n)
