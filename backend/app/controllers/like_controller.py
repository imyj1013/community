from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from . import __init__ as _
from ..models import user_model, post_model, like_model


async def create_like(request: Request, db: Session):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_like_create_request")
    try:
        post_id = body.get("post_id")
        user_id = body.get("user_id")

        if not post_id or not user_id:
            raise HTTPException(status_code=400, detail="invalid_like_create_request")

        post = post_model.get_post_by_id(db, post_id)
        user = user_model.get_user_by_id(db, user_id)
        if not post or not user:
            raise HTTPException(status_code=400, detail="invalid_like_create_request")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if session_user_id != user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        like_for_me = like_model.get_my_like(db, post_id, session_user_id)

        if like_for_me:
            raise HTTPException(status_code=400, detail="invalid_like_create_request")
        
        like = like_model.create_like(db, post_id, user_id)
        post = post_model.update_likes(db, post, 1)

        return JSONResponse(
            status_code=200,
            content={
                "detail": "like_create_success",
                "data": {"like_id": like.like_id},
            },
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")


async def delete_like(like_id: int, request: Request, db: Session):
    if like_id < 0:
        raise HTTPException(status_code=400, detail="invalid_like_delete_request")
    try:
        like = like_model.get_like_by_id(db, like_id)
        if not like:
            raise HTTPException(status_code=404, detail="like_not_found")
        
        post = post_model.get_post_by_id(db, like.post_id)
        if not post:
            raise HTTPException(status_code=400, detail="invalid_like_delete_request")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if like.user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        like_model.delete_like(db, like_id)
        post = post_model.update_likes(db, post, -1)

        return JSONResponse(status_code=200, content={"detail": "like_delete_success"})
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")
