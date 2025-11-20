from app import db

def create_like(post_id:int, user_id:int):
    like_id = db.counters["like"]
    db.counters["like"] += 1

    like = {
        "like_id": like_id,
        "post_id": post_id,
        "user_id": user_id,
    }
    db.likes_db.append(like)
    return like


def get_like_by_id(like_id: int):
    return next((l for l in db.likes_db if l["like_id"] == like_id), None)

def get_my_like(post_id, session_user_id):
    return next((l for l in db.likes_db if l["post_id"] == post_id and l["user_id"] == session_user_id), None)

def delete_like(like_id: int):
    db.likes_db = [l for l in db.likes_db if l["like_id"] != like_id]
    return
