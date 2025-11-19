from fastapi import FastAPI, Request , HTTPException, Response
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse
import re
import uuid
from datetime import datetime, timezone

app = FastAPI(title="Community API - Routes Only")

app.add_middleware(
    SessionMiddleware,
    secret_key="yourSecretKey",
    max_age=24 * 60 * 60,
    same_site="lax",
    https_only=False,
)

users_db = []
posts_db = []
comments_db = []
likes_db = []

user_id_seq = 1
post_id_seq = 1
comment_id_seq = 1
like_id_seq = 1

def find_user_by_email(email: str):
    return next((u for u in users_db if u["email"] == email), None)

def find_user_by_nickname(nickname: str):
    return next((u for u in users_db if u["nickname"] == nickname), None)

def find_user_by_id(user_id: int):
    return next((u for u in users_db if u["user_id"] == user_id), None)

def find_post_by_id(post_id: int):
    return next((p for p in posts_db if p["post_id"] == post_id), None)

def find_comment_by_id(comment_id: int):
    return next((c for c in comments_db if c["comment_id"] == comment_id), None)

def find_like_by_id(like_id: int):
    return next((l for l in likes_db if l["like_id"] == like_id), None)

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

@app.post("/user/login")
async def login(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_login_request")
    try:
        email = body.get("email")
        password = body.get("password")

        if not email or not password:
            raise HTTPException(status_code=400, detail="invalid_login_request")

        user = find_user_by_email(email)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_login_request")
        
        if user["password"] != password:
            raise HTTPException(status_code=401, detail="login_invalid_email_or_pwd")

        session_id = request.session.get("sessionID")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["sessionID"] = session_id
            request.session["email"] = email
            request.session["user_id"] = user["user_id"]
        else:
            raise HTTPException(status_code=409, detail="already_logged_in")

        return JSONResponse(
            status_code=200,
            content={
                "detail": "login_success",
                "data": {
                    "user_id": user["user_id"],
                    "profile_img_url": user.get("profile_image"),
                    "profile_nickname": user["nickname"],
                    "session_id": session_id
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="internal_server_error")
        

@app.post("/user/signup")
async def signup(request: Request):
    global user_id_seq
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_signup_request")
    try:
        email = body.get("email")
        password = body.get("password")
        nickname = body.get("nickname")
        profile_image = body.get("profile_image")

        if not email or not password or not nickname:
            raise HTTPException(status_code=400, detail="invalid_signup_request")
        
        if not email_is_valid(email):
            raise HTTPException(status_code=400, detail="invalid_signup_request")
        
        if not nickname_is_valid(nickname):
            raise HTTPException(status_code=400, detail="invalid_signup_request")

        user = {
            "user_id": user_id_seq,
            "email": email,
            "password": password,
            "nickname": nickname,
            "profile_image": profile_image,
        }
        users_db.append(user)
        user_id_seq += 1

        return JSONResponse(
            status_code=201,
            content={
                "detail": "register_success",
                "data": {
                    "user_id": user["user_id"]
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.get("/user/check-email")
async def check_email(email: str):
    try:
        valid = email_is_valid(email)
        if valid == True:
            exists = find_user_by_email(email) is not None
            return JSONResponse(
                status_code=200,
                content={
                    "detail": "email_check_success",
                    "data": {
                        "email": email,
                        "possible": not exists
                    }
                }
            )
        else :
            raise HTTPException(status_code=400, detail="invalid_email_format")
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.get("/user/check-nickname")
async def check_nickname(nickname: str):
    try:
        valid = nickname_is_valid(nickname)
        if valid == True:
            exists = find_user_by_nickname(nickname) is not None
            return JSONResponse(
                status_code=200,
                content={
                    "detail": "nickname_check_success",
                    "data": {
                        "nickname": nickname,
                        "possible": not exists
                    }
                }
            )
        else :
            raise HTTPException(status_code=400, detail="invalid_nickname_format")
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.put("/user/update-me/{user_id}")
async def update_me(user_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_profile_update_request")
    try:
        nickname = body.get("nickname")
        profile_image = body.get("profile_image")

        if nickname is None:
            raise HTTPException(status_code=400, detail="invalid_profile_update_request")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        user = find_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_profile_update_request")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        user["nickname"] = nickname
        if profile_image is not None:
            user["profile_image"] = profile_image

        return JSONResponse(
            status_code=200,
            content={
                "detail": "profile_update_success",
                "data": {
                    "user_id": user["user_id"],
                    "nickname": user["nickname"],
                    "profile_image": user.get("profile_image"),
                }
            }
        )
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.put("/user/update-password/{user_id}")
async def update_password(user_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_password_update_request")
    try:
        current_password = body.get("current_password")
        new_password = body.get("new_password")
        if not current_password:
            raise HTTPException(status_code=400, detail="invalid_password_update_request")
        if not new_password:
            raise HTTPException(status_code=400, detail="invalid_password_update_request")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        user = find_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_password_update_request")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        if user["password"] != current_password:
            raise HTTPException(status_code=400, detail="invalid_password")

        user["password"] = new_password
        return JSONResponse(status_code=200, content={"detail": "password_update_success"})
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.delete("/user/logout/{user_id}")
async def logout(user_id: int, request: Request):
    try:
        if not find_user_by_id(user_id):
            raise HTTPException(status_code=400, detail="invalid_logout_request")
    
        session_email = request.session.get("email")
        session_id = request.session.get("sessionID")
        session_user_id = request.session.get("user_id")

        if not session_email or not session_id or not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        request.session.clear()
        return JSONResponse(status_code=200, content={"detail": "logout_success"})
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.delete("/user/{user_id}")
async def delete_user(user_id: int, request: Request):
    global users_db
    try:
        if not find_user_by_id(user_id):
            raise HTTPException(status_code=400, detail="invalid_user_delete_request")
    
        session_email = request.session.get("email")
        session_id = request.session.get("sessionID")
        session_user_id = request.session.get("user_id")

        if not session_email or not session_id or not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        request.session.clear()
        
        users_db = [u for u in users_db if u["user_id"] != user_id]
        return JSONResponse(status_code=200, content={"detail": "user_delete_success"})
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")












@app.get("/posts")
async def list_posts(cursor_id: int, count: int):
    if count <= 0 or cursor_id < 0:
        raise HTTPException(status_code=400, detail="invalid_posts_list_request")
    try:
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
                    "views": format_number(p["views"]),
                    "comments_count": format_number(p["comments_count"]),
                    "likes": format_number(p["likes"]),
                }
            )
        return JSONResponse(
            status_code=200, 
            content={
                "detail": "posts_list_success", 
                "data":{
                    "post_list": data_list,
                    "next_cursor": next_cursor
                }
            }
        )
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.post("/posts")
async def create_post(request: Request):
    global post_id_seq

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_post_create_request")
    try:
        user_id = body.get("user_id")
        title = body.get("title")
        content = body.get("content")
        image_url = body.get("image_url")

        if not user_id or not title or not content:
            raise HTTPException(status_code=400, detail="invalid_post_create_request")
        
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        user = find_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_post_create_request")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        post = {
            "post_id": post_id_seq,
            "user_id": user_id,
            "title": title,
            "content": content,
            "image_url": image_url,
            "author_nickname": user["nickname"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "views": 0,
            "comments_count": 0,
            "likes": 0,
        }
        posts_db.append(post)
        post_id_seq += 1

        return JSONResponse(
            status_code=201, 
            content={
                "detail": "post_create_success", 
                "data":{"post_id": post["post_id"]}
            }
        )
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")



@app.put("/posts/{post_id}")
async def update_post(post_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_post_update_request")
    try:
        user_id = body.get("user_id")
        title = body.get("title")
        content = body.get("content")
        image_url = body.get("image_url")

        if not user_id or not title or not content:
            raise HTTPException(status_code=400, detail="invalid_post_update_request")

        post = find_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="post_not_found")
        
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        user = find_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_post_update_request")
        
        if post["user_id"] != request.session["user_id"]:
            raise HTTPException(status_code=403, detail="forbidden_user")

        post["title"] = title
        post["content"] = content
        post["image_url"] = image_url
        post["updated_at"] = datetime.now(timezone.utc).isoformat()

        return JSONResponse(
            status_code=200,
            content={
                "detail": "post_update_success",
                "data": {
                    "post_id": post_id
                }
            }
        )
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.get("/posts/{post_id}")
async def get_post_detail(post_id: int, request:Request):
    if post_id < 0:
        raise HTTPException(status_code=400, detail="invalid_posts_detail_request")

    post = find_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")
    try:
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        post_comments = [c for c in comments_db if c["post_id"] == post_id]
        like_for_me = next((l for l in likes_db if l["post_id"] == post_id and l["user_id"] == session_user_id),None)

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
        
        post["views"] += 1

        return JSONResponse(
            status_code=200,
            content={
                "detail": "post_detail_success",
                "data": {
                    "post_id": post["post_id"],
                    "title": post["title"],
                    "content": post["content"],
                    "image_url": post["image_url"],
                    "author_nickname": post["author_nickname"],
                    "created_at": post["created_at"],
                    "updated_at": post["updated_at"],
                    "views": post["views"],
                    "likes": post["likes"],
                    "comments_count": post["comments_count"],
                    "comments": comments_json,
                    "is_liked_by_me": like_for_me is not None,
                    "like_id": like_for_me["like_id"] if like_for_me else None
                }
            }
        )
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, request:Request):
    global posts_db
    if post_id < 0:
        raise HTTPException(status_code=400, detail="invalid_post_delete_request")

    post = find_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")
    
    try:
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        if post["user_id"] != request.session["user_id"]:
            raise HTTPException(status_code=403, detail="forbidden_user")

        posts_db = [p for p in posts_db if p["post_id"] != post_id]
        return JSONResponse(status_code=200, content={"detail": "post_delete_success"})
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")











@app.post("/comment")
async def create_comment(request: Request):
    global comment_id_seq

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_comment_create_request")
    try:
        post_id = body.get("post_id")
        user_id = body.get("user_id")
        content = body.get("content")

        if not post_id or not user_id or not content:
            raise HTTPException(status_code=400, detail="invalid_comment_create_request")

        if not find_post_by_id(post_id) or not find_user_by_id(user_id):
            raise HTTPException(status_code=400, detail="invalid_comment_create_request")
        
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=400, detail="invalid_comment_create_request")
            
        comment = {
            "comment_id": comment_id_seq,
            "post_id": post_id,
            "user_id": user_id,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        comments_db.append(comment)
        comment_id_seq += 1

        post = find_post_by_id(post_id)
        post["comments_count"] += 1

        return JSONResponse(
            status_code=201, 
            content={
                "detail": "comment_create_success",
                "data": {"comment_id": comment["comment_id"]}
            }
        )
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.put("/comment/{comment_id}")
async def update_comment(comment_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_comment_update_request")
    try:
        content = body.get("content")
        if not content:
            raise HTTPException(status_code=400, detail="invalid_comment_update_request")

        comment = find_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="comment_not_found")
        
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        if comment["user_id"] != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        comment["content"] = content

        return JSONResponse(
            status_code=200, 
            content={
                "detail": "comment_update_success",
                "data": {"comment_id": comment["comment_id"]}
            }
        )
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.delete("/comment/{comment_id}")
async def delete_comment(comment_id: int, request:Request):
    global comments_db
    if comment_id < 0:
        raise HTTPException(status_code=400, detail="invalid_comment_delete_request")
    try:
        comment = find_comment_by_id(comment_id)
        if not comment:
                raise HTTPException(status_code=404, detail="comment_not_found")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        if comment["user_id"] != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        comments_db = [c for c in comments_db if c["comment_id"] != comment_id]

        post = find_post_by_id(comment["post_id"])
        post["comments_count"] -= 1

        return JSONResponse(status_code=200, content={"detail": "comment_delete_success"})
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.post("/like")
async def create_like(request: Request):
    global like_id_seq

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_like_create_request")
    try:
        post_id = body.get("post_id")
        user_id = body.get("user_id")

        if not post_id or not user_id:
            raise HTTPException(status_code=400, detail="invalid_like_create_request")

        if not find_post_by_id(post_id) or not find_user_by_id(user_id):
            raise HTTPException(status_code=400, detail="invalid_like_create_request")
        
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        if session_user_id != user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        like_for_me = next((l for l in likes_db if l["post_id"] == post_id and l["user_id"] == session_user_id),None)

        if like_for_me:
            raise HTTPException(status_code=400, detail="invalid_like_create_request")

        like = {
            "like_id": like_id_seq,
            "post_id": post_id,
            "user_id": user_id,
        }
        likes_db.append(like)
        like_id_seq += 1

        post = find_post_by_id(post_id)
        post["likes"] += 1

        return JSONResponse(
            status_code=200, 
            content={
                "detail": "like_create_success",
                "data": {"like_id": like["like_id"]}
            }
        )
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


@app.delete("/like/{like_id}")
async def delete_like(like_id: int, request:Request):
    global likes_db
    if like_id < 0:
        raise HTTPException(status_code=400, detail="invalid_like_delete_request")
    try:
        like = find_like_by_id(like_id)
        if not like:
                raise HTTPException(status_code=404, detail="like_not_found")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        if like["user_id"] != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        likes_db = [l for l in likes_db if l["like_id"] != like_id]

        post = find_post_by_id(like["post_id"])
        post["likes"] -= 1

        return JSONResponse(status_code=200, content={"detail": "like_delete_success"})
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")
