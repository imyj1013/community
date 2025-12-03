from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import traceback
from . import __init__ as _
from ..models import user_model, post_model, comment_model

async def create_comment(request: Request, db: AsyncSession):
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
        
        post = await post_model.get_post_by_id(db, post_id)
        user = await user_model.get_user_by_id(db, user_id)
        if not post or not user:
            raise HTTPException(status_code=400, detail="invalid_comment_create_request")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if user_id != session_user_id:
            raise HTTPException(status_code=400, detail="invalid_comment_create_request")

        comment = await comment_model.create_comment(db, post_id, user_id, content)
        post = await post_model.update_comments_count(db, post, 1)

        return JSONResponse(
            status_code=201,
            content={
                "detail": "comment_create_success",
                "data": {"comment_id": comment.comment_id},
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[comment-create] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def update_comment(comment_id: int, request: Request, db: AsyncSession):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_comment_update_request")
    try:
        content = body.get("content")
        if not content:
            raise HTTPException(status_code=400, detail="invalid_comment_update_request")

        comment = await comment_model.get_comment_by_id(db, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="comment_not_found")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if comment.user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        comment = await comment_model.update_comment(db, comment, content)

        return JSONResponse(
            status_code=200,
            content={
                "detail": "comment_update_success",
                "data": {"comment_id": comment.comment_id},
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[update-comment] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def delete_comment(comment_id: int, request: Request, db: AsyncSession):
    if comment_id < 0:
        raise HTTPException(status_code=400, detail="invalid_comment_delete_request")
    try:
        comment = await comment_model.get_comment_by_id(db, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="comment_not_found")

        post = await post_model.get_post_by_id(db, comment.post_id)
        if not post:
            raise HTTPException(status_code=400, detail="invalid_comment_delete_request")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if comment.user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        await comment_model.delete_comment(db, comment_id)
        post = await post_model.update_comments_count(db, post, -1)

        return JSONResponse(status_code=200, content={"detail": "comment_delete_success"})
    except HTTPException:
        raise
    except Exception as e:
        print("[delete-comment] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")
