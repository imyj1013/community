from app import db

def create_user(email: str, password: str, nickname: str, profile_image: str | None):
    user_id = db.counters["user"]
    db.counters["user"] += 1

    user = {
        "user_id": user_id,
        "email": email,
        "password": password,
        "nickname": nickname,
        "profile_image": profile_image,
    }
    db.users_db.append(user)
    return user

def get_user_by_email(email: str):
    return next((u for u in db.users_db if u["email"] == email), None)

def get_user_by_nickname(nickname: str):
    return next((u for u in db.users_db if u["nickname"] == nickname), None)

def get_user_by_id(user_id: int):
    return next((u for u in db.users_db if u["user_id"] == user_id), None)

def update_user_profile(user: dict, nickname: str, profile_image: str | None):
    user["nickname"] = nickname
    if profile_image is not None:
        user["profile_image"] = profile_image
    return user

def update_user_password(user: dict, new_password: str):
    user["password"] = new_password
    return user

def delete_user(user_id: int):
    db.users_db = [u for u in db.users_db if u["user_id"] != user_id]
    return
