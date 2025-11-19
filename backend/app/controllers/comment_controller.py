from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from . import __init__ as _
from app import db, utils

async def create_comment(request: Request):
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

        if not utils.find_post_by_id(post_id) or not utils.find_user_by_id(user_id):
            raise HTTPException(status_code=400, detail="invalid_comment_create_request")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if user_id != session_user_id:
            raise HTTPException(status_code=400, detail="invalid_comment_create_request")

        comment_id = db.counters["comment"]
        db.counters["comment"] += 1

        comment = {
            "comment_id": comment_id,
            "post_id": post_id,
            "user_id": user_id,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        db.comments_db.append(comment)

        post = utils.find_post_by_id(post_id)
        post["comments_count"] += 1

        return JSONResponse(
            status_code=201,
            content={
                "detail": "comment_create_success",
                "data": {"comment_id": comment["comment_id"]},
            },
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")


async def update_comment(comment_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_comment_update_request")
    try:
        content = body.get("content")
        if not content:
            raise HTTPException(status_code=400, detail="invalid_comment_update_request")

        comment = utils.find_comment_by_id(comment_id)
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
                "data": {"comment_id": comment["comment_id"]},
            },
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")


async def delete_comment(comment_id: int, request: Request):
    if comment_id < 0:
        raise HTTPException(status_code=400, detail="invalid_comment_delete_request")
    try:
        comment = utils.find_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="comment_not_found")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if comment["user_id"] != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        db.comments_db = [c for c in db.comments_db if c["comment_id"] != comment_id]

        post = utils.find_post_by_id(comment["post_id"])
        post["comments_count"] -= 1

        return JSONResponse(status_code=200, content={"detail": "comment_delete_success"})
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")
