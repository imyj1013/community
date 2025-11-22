from app import db

def create_comment(post_id, user_id, content, created_at):
    comment_id = db.counters["comment"]
    db.counters["comment"] += 1

    comment = {
        "comment_id": comment_id,
        "post_id": post_id,
        "user_id": user_id,
        "content": content,
        "created_at": created_at
    }
    db.comments_db.append(comment)
    return comment

def get_comment_by_id(comment_id: int):
    return next((c for c in db.comments_db if c["comment_id"] == comment_id), None)

def update_comment(comment, content):
    comment["content"] = content
    return comment

def delete_comment(comment_id):
    db.comments_db = [c for c in db.comments_db if c["comment_id"] != comment_id]
    return

def get_comment_by_post_id(post_id:int):
    return [c for c in db.comments_db if c["post_id"] == post_id]
