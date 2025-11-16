# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Community API - Step1 (Routes Only, No Pydantic)")


# 인메모리 "DB"
users_db = []       # {user_id, email, password, nickname, profile_image}
posts_db = []       # {post_id, user_id, title, content, ...}
comments_db = []    # {comment_id, post_id, user_id, content, created_at}
likes_db = []       # {like_id, post_id, user_id}

user_id_seq = 1
post_id_seq = 1
comment_id_seq = 1
like_id_seq = 1


# 유틸 함수
def find_user_by_email(email: str):
    return next((u for u in users_db if u["email"] == email), None)


def find_user_by_id(user_id: int):
    return next((u for u in users_db if u["user_id"] == user_id), None)


def find_post_by_id(post_id: int):
    return next((p for p in posts_db if p["post_id"] == post_id), None)


def find_comment_by_id(comment_id: int):
    return next((c for c in comments_db if c["comment_id"] == comment_id), None)


def find_like_by_id(like_id: int):
    return next((l for l in likes_db if l["like_id"] == like_id), None)


# 로그인  POST /user/login
@app.post("/user/login")
async def login(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_login_request", "data": None},
        )

    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_login_request", "data": None},
        )

    user = find_user_by_email(email)
    if not user or user["password"] != password:
        return JSONResponse(
            status_code=401,
            content={"message": "login_invalid_email_or_pwd", "data": None},
        )

    return {
        "message": "login_success",
        "data": {
            "user_id": user["user_id"],
            "profile_img_url": user.get("profile_image"),
            "profile_nickname": user["nickname"],
        },
    }


# 회원가입  POST /user/signup
@app.post("/user/signup", status_code=201)
async def signup(request: Request):
    global user_id_seq

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_signup_request", "data": None},
        )

    email = body.get("email")
    password = body.get("password")
    nickname = body.get("nickname")
    profile_image = body.get("profile_image")

    if not email or not password or not nickname:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_signup_request", "data": None},
        )

    if find_user_by_email(email):
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_signup_request", "data": None},
        )

    user = {
        "user_id": user_id_seq,
        "email": email,
        "password": password,
        "nickname": nickname,
        "profile_image": profile_image,
    }
    users_db.append(user)
    user_id_seq += 1

    return {
        "message": "register_success",
        "data": {"user_id": user["user_id"]},
    }


# 이메일 중복확인  GET /user/check-email/{email}
@app.get("/user/check-email/{email}")
async def check_email(email: str):
    exists = find_user_by_email(email) is not None
    return {
        "message": "email_check_success",
        "data": {
            "email": email,
            "possible": not exists,
        },
    }


# 닉네임 중복확인  GET /user/check-nickname/{nickname}
@app.get("/user/check-nickname/{nickname}")
async def check_nickname(nickname: str):
    exists = any(u["nickname"] == nickname for u in users_db)
    return {
        "message": "nickname_check_success",
        "data": {
            "nickname": nickname,
            "possible": not exists,
        },
    }


# 회원정보수정  PUT /user/update-me/{user_id}
@app.put("/user/update-me/{user_id}")
async def update_me(user_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_profile_update_request", "data": None},
        )

    nickname = body.get("nickname")
    profile_image = body.get("profile_image")

    if nickname is None:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_profile_update_request", "data": None},
        )

    user = find_user_by_id(user_id)
    if not user:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_profile_update_request", "data": None},
        )

    user["nickname"] = nickname
    if profile_image is not None:
        user["profile_image"] = profile_image

    return {
        "message": "profile_update_success",
        "data": {
            "user_id": user["user_id"],
            "nickname": user["nickname"],
            "profile_image": user.get("profile_image"),
        },
    }


# 비밀번호수정  PUT /user/update-password/{user_id}
@app.put("/user/update-password/{user_id}")
async def update_password(user_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_password_update_request", "data": None},
        )

    new_password = body.get("new_password")
    if not new_password:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_password_update_request", "data": None},
        )

    user = find_user_by_id(user_id)
    if not user:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_password_update_request", "data": None},
        )

    user["password"] = new_password
    return {"message": "password_update_success", "data": None}


# 회원탈퇴  DELETE /user/{user_id}
@app.delete("/user/{user_id}")
async def delete_user(user_id: int):
    global users_db
    user = find_user_by_id(user_id)
    if not user:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_user_delete_request", "data": None},
        )

    users_db = [u for u in users_db if u["user_id"] != user_id]
    return {"message": "user_delete_success", "data": None}


# 게시글 목록 조회  GET /posts/{cursor_id}/{count}
@app.get("/posts/{cursor_id}/{count}")
async def list_posts(cursor_id: int, count: int):
    if count <= 0:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_posts_list_request", "data": None},
        )

    filtered = [p for p in posts_db if p["post_id"] > cursor_id]
    sliced = filtered[:count]
    next_cursor = sliced[-1]["post_id"] if sliced else cursor_id

    data_list = []
    for p in sliced:
        data_list.append(
            {
                "post_id": p["post_id"],
                "title": p["title"][:26],
                "author_nickname": p["author_nickname"],
                "created_at": p["created_at"],
                "views": p["views"],
                "comments_count": p["comments_count"],
                "likes": p["likes"],
            }
        )

    return {
        "message": "posts_list_success",
        "data": data_list,
        "next_cursor": next_cursor,
    }


# 게시글 등록  POST /posts
@app.post("/posts", status_code=201)
async def create_post(request: Request):
    global post_id_seq

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_post_create_request", "data": None},
        )

    user_id = body.get("user_id")
    title = body.get("title")
    content = body.get("content")
    image_url = body.get("image_url")

    if not user_id or not title or not content:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_post_create_request", "data": None},
        )

    user = find_user_by_id(user_id)
    if not user:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_post_create_request", "data": None},
        )

    post = {
        "post_id": post_id_seq,
        "user_id": user_id,
        "title": title,
        "content": content,
        "image_url": image_url,
        "author_nickname": user["nickname"],
        "created_at": "2023-11-03 10:00:00",
        "updated_at": "2023-11-03 10:00:00",
        "views": "0",
        "comments_count": "0",
        "likes": "0",
    }
    posts_db.append(post)
    post_id_seq += 1

    return {
        "message": "post_create_success",
        "data": {"post_id": post["post_id"]},
    }


# 게시글 수정  PUT /posts/{post_id}
@app.put("/posts/{post_id}")
async def update_post(post_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_post_update_request", "data": None},
        )

    user_id = body.get("user_id")
    title = body.get("title")
    content = body.get("content")
    image_url = body.get("image_url")

    post = find_post_by_id(post_id)
    if not post:
        return JSONResponse(
            status_code=404,
            content={"message": "post_not_found", "data": None},
        )

    if not user_id or not title or not content:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_post_update_request", "data": None},
        )

    post["title"] = title
    post["content"] = content
    post["image_url"] = image_url
    post["updated_at"] = "2023-11-03 11:00:00"

    return {
        "message": "post_update_success",
        "data": {"post_id": post_id},
    }


# 게시글 상세조회  GET /posts/{post_id}
@app.get("/posts/{post_id}")
async def get_post_detail(post_id: int):
    post = find_post_by_id(post_id)
    if not post:
        return JSONResponse(
            status_code=404,
            content={"message": "post_not_found", "data": None},
        )

    current_user_id = 1

    post_comments = [c for c in comments_db if c["post_id"] == post_id]
    post_likes = [l for l in likes_db if l["post_id"] == post_id]
    like_for_me = next(
        (l for l in post_likes if l["user_id"] == current_user_id), None
    )

    comments_json = []
    for c in post_comments:
        author = find_user_by_id(c["user_id"])
        nickname = author["nickname"] if author else "unknown"
        comments_json.append(
            {
                "comment_id": c["comment_id"],
                "content": c["content"],
                "author_nickname": nickname,
                "created_at": c["created_at"],
            }
        )

    return {
        "message": "post_detail_success",
        "data": {
            "post_id": post["post_id"],
            "title": post["title"],
            "content": post["content"],
            "image_url": post["image_url"],
            "author_nickname": post["author_nickname"],
            "created_at": post["created_at"],
            "updated_at": post["updated_at"],
            "views": 1234,
            "likes": len(post_likes),
            "comments_count": len(post_comments),
            "comments": comments_json,
            "is_liked_by_me": like_for_me is not None,
            "like_id": like_for_me["like_id"] if like_for_me else 1,
        },
    }


# 게시글 삭제  DELETE /posts/{post_id}
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    global posts_db
    post = find_post_by_id(post_id)
    if not post:
        return JSONResponse(
            status_code=404,
            content={"message": "post_not_found", "data": None},
        )

    posts_db = [p for p in posts_db if p["post_id"] != post_id]
    return {"message": "post_delete_success", "data": None}


# 댓글 등록  POST /comment
@app.post("/comment", status_code=201)
async def create_comment(request: Request):
    global comment_id_seq

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_comment_create_request", "data": None},
        )

    post_id = body.get("post_id")
    user_id = body.get("user_id")
    content = body.get("content")

    if not post_id or not user_id or not content:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_comment_create_request", "data": None},
        )

    if not find_post_by_id(post_id) or not find_user_by_id(user_id):
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_comment_create_request", "data": None},
        )

    comment = {
        "comment_id": comment_id_seq,
        "post_id": post_id,
        "user_id": user_id,
        "content": content,
        "created_at": "2023-11-03 10:30:00",
    }
    comments_db.append(comment)
    comment_id_seq += 1

    return {
        "message": "comment_create_success",
        "data": {"comment_id": comment["comment_id"]},
    }


# 댓글 수정  PUT /comment/{comment_id}
@app.put("/comment/{comment_id}")
async def update_comment(comment_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_comment_update_request", "data": None},
        )

    content = body.get("content")
    if not content:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_comment_update_request", "data": None},
        )

    comment = find_comment_by_id(comment_id)
    if not comment:
        return JSONResponse(
            status_code=404,
            content={"message": "comment_not_found", "data": None},
        )

    comment["content"] = content
    return {
        "message": "comment_update_success",
        "data": {"comment_id": comment_id},
    }


# 댓글 삭제  DELETE /comment/{comment_id}
@app.delete("/comment/{comment_id}")
async def delete_comment(comment_id: int):
    global comments_db
    comment = find_comment_by_id(comment_id)
    if not comment:
        return JSONResponse(
            status_code=404,
            content={"message": "comment_not_found", "data": None},
        )

    comments_db = [c for c in comments_db if c["comment_id"] != comment_id]
    return {"message": "comment_delete_success", "data": None}


# 좋아요 등록  POST /like
@app.post("/like", status_code=201)
async def create_like(request: Request):
    global like_id_seq

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_like_create_request", "data": None},
        )

    post_id = body.get("post_id")
    user_id = body.get("user_id")

    if not post_id or not user_id:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_like_create_request", "data": None},
        )

    if not find_post_by_id(post_id) or not find_user_by_id(user_id):
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_like_create_request", "data": None},
        )

    existing = next(
        (
            l
            for l in likes_db
            if l["post_id"] == post_id and l["user_id"] == user_id
        ),
        None,
    )
    if existing:
        return JSONResponse(
            status_code=400,
            content={"message": "invalid_like_create_request", "data": None},
        )

    like = {
        "like_id": like_id_seq,
        "post_id": post_id,
        "user_id": user_id,
    }
    likes_db.append(like)
    like_id_seq += 1

    return {
        "message": "like_create_success",
        "data": {"like_id": like["like_id"]},
    }


# 좋아요 취소  DELETE /like/{like_id}
@app.delete("/like/{like_id}")
async def delete_like(like_id: int):
    global likes_db
    like = find_like_by_id(like_id)
    if not like:
        return JSONResponse(
            status_code=404,
            content={"message": "like_not_found", "data": None},
        )

    likes_db = [l for l in likes_db if l["like_id"] != like_id]
    return {"message": "like_delete_success", "data": None}
