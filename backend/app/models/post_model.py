from app import db

def create_post(user_id, title, content, summary, image_url, nickname, time):
    post_id = db.counters["post"]
    db.counters["post"] += 1

    post = {
        "post_id": post_id,
        "user_id": user_id,
        "title": title,
        "content": content,
        "summary": summary,
        "image_url": image_url,
        "author_nickname": nickname,
        "created_at": time,
        "updated_at": time,
        "views": 0,
        "comments_count": 0,
        "likes": 0
    }
    db.posts_db.append(post)
    return post


def get_post_by_id(post_id: int):
    return next((p for p in db.posts_db if p["post_id"] == post_id), None)

def get_post_list_by_id(cursor_id: int):
    return [p for p in db.posts_db if p["post_id"] > cursor_id]

def update_post(post, title, content, summary, image_url, time):
    post["title"] = title
    post["content"] = content
    post["summary"] = summary
    post["image_url"] = image_url
    post["updated_at"] = time
    return post

def delete_post(post_id:int):
    db.posts_db = [p for p in db.posts_db if p["post_id"] != post_id]
    return

def update_likes(post, count):
    post["likes"] = post["likes"] + count
    return post

def update_comments_count(post, count):
    post["comments_count"] = post["comments_count"] + count
    return post