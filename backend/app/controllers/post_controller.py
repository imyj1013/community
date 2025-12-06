from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import traceback
from . import __init__ as _
from ..models import user_model, post_model, comment_model, like_model
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_path = "./ai/kobart-summary-v3"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

async def list_posts(cursor_id: int, count: int, db: AsyncSession):
    if count <= 0 or cursor_id < 0:
        raise HTTPException(status_code=400, detail="invalid_posts_list_request")
    try:
        filtered = await post_model.get_post_list_by_id(db, cursor_id)
        sliced = filtered[:count]
        next_cursor = sliced[-1].post_id if sliced else cursor_id

        data_list = []
        for p in sliced:
            author = await user_model.get_user_by_id(db, p.user_id)
            data_list.append(
                {
                    "post_id": p.post_id,
                    "title": p.title,
                    "author_nickname": author.nickname,
                    "author_profile_image": author.profile_image,
                    "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
                    "summary": p.summary,
                    "views": p.views,
                    "comments_count": p.comments_count,
                    "likes": p.likes,
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
    except Exception as e:
        print("[post-list] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def create_post(request: Request, db: AsyncSession):
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

        user = await user_model.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_post_create_request")

        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        inputs = tokenizer(content, return_tensors="pt")
        summary_ids = model.generate(**inputs, max_length=200)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        post = await post_model.create_post(db, user_id, title, content, summary, image_url, user.nickname)

        return JSONResponse(
            status_code=201,
            content={"detail": "post_create_success", "data": {"post_id": post.post_id}},
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[create-post] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def update_post(post_id: int, request: Request, db: AsyncSession):
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

        post = await post_model.get_post_by_id(db, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="post_not_found")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        user = await user_model.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_post_update_request")

        if post.user_id != request.session["user_id"]:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        inputs = tokenizer(content, return_tensors="pt")
        summary_ids = model.generate(**inputs, max_length=200)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        post = await post_model.update_post(db, post, title, content, summary, image_url)

        return JSONResponse(
            status_code=200,
            content={"detail": "post_update_success", "data": {"post_id": post_id}},
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[update-post] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def get_post_detail(post_id: int, request: Request, db: AsyncSession):
    if post_id < 0:
        raise HTTPException(status_code=400, detail="invalid_posts_detail_request")

    post = await post_model.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")
    try:
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        post_comments = await comment_model.get_comment_by_post_id(db, post_id)
        like_for_me = await like_model.get_my_like(db, post_id, session_user_id)

        comments_json = []
        for c in post_comments:
            author = await user_model.get_user_by_id(db, c.user_id)
            comments_json.append(
                {
                    "comment_id": c.comment_id,
                    "content": c.content,
                    "author_nickname": author.nickname,
                    "author_profile_image": author.profile_image,
                    "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None,
                    "user_id": c.user_id,
                }
            )

        await post_model.update_views(db, post)
        author = await user_model.get_user_by_id(db, post.user_id)

        return JSONResponse(
            status_code=200,
            content={
                "detail": "post_detail_success",
                "data": {
                    "post_id": post.post_id,
                    "title": post.title,
                    "content": post.content,
                    "image_url": getattr(post, "image_url", None),
                    "author_nickname": author.nickname,
                    "author_user_id": post.user_id,
                    "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S") if post.created_at else None,
                    "updated_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S") if post.created_at else None,
                    "views": post.views,
                    "likes": post.likes,
                    "comments_count": post.comments_count,
                    "comments": comments_json,
                    "is_liked_by_me": like_for_me is not None,
                    "like_id": like_for_me.like_id if like_for_me else None,
                },
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[post-detail] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def delete_post(post_id: int, request: Request, db: AsyncSession):
    if post_id < 0:
        raise HTTPException(status_code=400, detail="invalid_post_delete_request")

    post = await post_model.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")
    try:
        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if post.user_id != request.session["user_id"]:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        await post_model.delete_post(db, post_id)
        return JSONResponse(status_code=200, content={"detail": "post_delete_success"})
    except HTTPException:
        raise
    except Exception as e:
        print("[delete-post] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")
