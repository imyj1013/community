from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from . import __init__ as _
from app import db, utils

async def create_like(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_like_create_request")
    try:
        post_id = body.get("post_id")
        user_id = body.get("user_id")

        if not post_id or not user_id:
            raise HTTPException(status_code=400, detail="invalid_like_create_request")

        if not utils.find_post_by_id(post_id) or not utils.find_user_by_id(user_id):
            raise HTTPException(status_code=400, detail="invalid_like_create_request")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if session_user_id != user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        like_for_me = next(
            (l for l in db.likes_db if l["post_id"] == post_id and l["user_id"] == session_user_id),
            None,
        )

        if like_for_me:
            raise HTTPException(status_code=400, detail="invalid_like_create_request")

        like_id = db.counters["like"]
        db.counters["like"] += 1

        like = {
            "like_id": like_id,
            "post_id": post_id,
            "user_id": user_id,
        }
        db.likes_db.append(like)

        post = utils.find_post_by_id(post_id)
        post["likes"] += 1

        return JSONResponse(
            status_code=200,
            content={
                "detail": "like_create_success",
                "data": {"like_id": like["like_id"]},
            },
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")


async def delete_like(like_id: int, request: Request):
    if like_id < 0:
        raise HTTPException(status_code=400, detail="invalid_like_delete_request")
    try:
        like = utils.find_like_by_id(like_id)
        if not like:
            raise HTTPException(status_code=404, detail="like_not_found")

        session_user_id = request.session.get("user_id")
        if not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")

        if like["user_id"] != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        db.likes_db = [l for l in db.likes_db if l["like_id"] != like_id]

        post = utils.find_post_by_id(like["post_id"])
        post["likes"] -= 1

        return JSONResponse(status_code=200, content={"detail": "like_delete_success"})
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal_server_error")
