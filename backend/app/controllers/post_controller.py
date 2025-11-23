from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from . import __init__ as _
from app import db, utils
from app.models import user_model, post_model, comment_model, like_model
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_path = "./ai/kobart-summary-v3"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

async def list_posts(cursor_id: int, count: int):
    if count <= 0 or cursor_id < 0:
        raise HTTPException(status_code=400, detail="invalid_posts_list_request")
    try:
        filtered = [p for p in db.posts_db if p["post_id"] > cursor_id]
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
                    "summary": p["summary"],
                    "views": utils.format_number(p["views"]),
                    "comments_count": utils.format_number(p["comments_count"]),
                    "likes": utils.format_number(p["likes"]),
                }
            )
        return JSONResponse(
            status_code=200,
            content={
                "detail": "posts_list_success",
                "data": {"post_list": data_list, "next_cursor": next_cursor},
            },
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")


async def create_post(request: Request):
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

        user = user_model.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_post_create_request")

        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        inputs = tokenizer(content, return_tensors="pt")
        summary_ids = model.generate(**inputs, max_length=200)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        post = post_model.create_post(user_id, title, content, summary, image_url, user["nickname"], datetime.now(timezone.utc).isoformat())

        return JSONResponse(
            status_code=201,
            content={"detail": "post_create_success", "data": {"post_id": post["post_id"]}},
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")


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

        post = post_model.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="post_not_found")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        user = user_model.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_post_update_request")

        if post["user_id"] != request.session["user_id"]:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        inputs = tokenizer(content, return_tensors="pt")
        summary_ids = model.generate(**inputs, max_length=200)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        post = post_model.update_post(post, title, content, summary, image_url, datetime.now(timezone.utc).isoformat())

        return JSONResponse(
            status_code=200,
            content={"detail": "post_update_success", "data": {"post_id": post_id}},
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")


async def get_post_detail(post_id: int, request: Request):
    if post_id < 0:
        raise HTTPException(status_code=400, detail="invalid_posts_detail_request")

    post = post_model.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")
    try:
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        post_comments = comment_model.get_comment_by_post_id(post_id)
        like_for_me = like_model.get_my_like(post_id, session_user_id)

        comments_json = []
        for c in post_comments:
            author = user_model.get_user_by_id(c["user_id"])
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
                    "like_id": like_for_me["like_id"] if like_for_me else None,
                },
            },
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")


async def delete_post(post_id: int, request: Request):
    if post_id < 0:
        raise HTTPException(status_code=400, detail="invalid_post_delete_request")

    post = post_model.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")
    try:
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if post["user_id"] != request.session["user_id"]:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        db.posts_db = delete_post(post_id)
        return JSONResponse(status_code=200, content={"detail": "post_delete_success"})
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")
