from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from . import __init__ as _
from models import user_model, post_model, comment_model

async def create_comment(request: Request, db: Session):
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

        if not post_model.get_post_by_id(db, post_id) or not user_model.get_user_by_id(db, user_id):
            raise HTTPException(status_code=400, detail="invalid_comment_create_request")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if user_id != session_user_id:
            raise HTTPException(status_code=400, detail="invalid_comment_create_request")

        comment = comment_model.create_comment(post_id, user_id, content)
        post = post_model.update_comments_count(db, post, 1)

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


async def update_comment(comment_id: int, request: Request, db: Session):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_comment_update_request")
    try:
        content = body.get("content")
        if not content:
            raise HTTPException(status_code=400, detail="invalid_comment_update_request")

        comment = comment_model.get_comment_by_id(db, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="comment_not_found")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if comment["user_id"] != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        comment = comment_model.update_comment(db, comment, content)

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


async def delete_comment(comment_id: int, request: Request, db: Session):
    if comment_id < 0:
        raise HTTPException(status_code=400, detail="invalid_comment_delete_request")
    try:
        comment = comment_model.get_comment_by_id(db, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="comment_not_found")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if comment["user_id"] != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        comment_model.delete_comment(db, comment_id)
        post = post_model.update_comments_count(db, post, -1)

        return JSONResponse(status_code=200, content={"detail": "comment_delete_success"})
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")
