from fastapi import Request, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import traceback
import os
import uuid
from . import __init__ as _
from .. import utils
from ..models import user_model

async def login(request: Request, db: AsyncSession):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_login_request")
    try:
        email = body.get("email")
        password = body.get("password")

        if not email or not password:
            raise HTTPException(status_code=400, detail="invalid_login_request")

        user = await user_model.get_user_by_email(db, email)        
        if not user or not await utils.verify_password_async(password, user.password):
            raise HTTPException(status_code=401, detail="login_invalid_email_or_pwd")

        session_id = request.session.get("sessionID")
        session_email = request.session.get("email")
        session_user_id = request.session.get("user_id")

        if session_id and session_email == email and session_user_id == user.user_id:
            return JSONResponse(
                status_code=200,
                content={
                    "detail": "login_success",
                    "data": {
                        "user_id": user.user_id,
                        "profile_img_url": getattr(user, "profile_image", None),
                        "profile_nickname": user.nickname,
                        "session_id": session_id,
                    },
                },
            )

        if session_id and session_user_id != user.user_id:
            request.session.clear()

        new_session_id = str(uuid.uuid4())
        request.session["sessionID"] = new_session_id
        request.session["email"] = email
        request.session["user_id"] = user.user_id

        return JSONResponse(
            status_code=200,
            content={
                "detail": "login_success",
                "data": {
                    "user_id": user.user_id,
                    "profile_img_url": getattr(user, "profile_image", None),
                    "profile_nickname": user.nickname,
                    "session_id": new_session_id,
                },
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[login] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")
        

async def signup(request: Request, db: AsyncSession):
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
        
        if not utils.email_is_valid(email):
            raise HTTPException(status_code=400, detail="invalid_signup_request")
        
        if not utils.nickname_is_valid(nickname):
            raise HTTPException(status_code=400, detail="invalid_signup_request")

        if await user_model.get_user_by_email(db, email):
            raise HTTPException(status_code=400, detail="invalid_signup_request")

        hashed_password = await utils.hash_password_async(password)

        user = await user_model.create_user(db, email, hashed_password, nickname, profile_image)

        return JSONResponse(
            status_code=201,
            content={
                "detail": "register_success",
                "data": {
                    "user_id": user.user_id
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[signup] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def check_email(email: str, db: AsyncSession):
    try:
        valid = utils.email_is_valid(email)
        if valid == True:
            exists = await user_model.get_user_by_email(db, email) is not None
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
    except Exception as e:
        print("[check-email] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def check_nickname(nickname: str, db: AsyncSession):
    try:
        valid = utils.nickname_is_valid(nickname)
        if valid:
            exists = await user_model.get_user_by_nickname(db, nickname) is not None
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
    except Exception as e:
        print("[check-nickname] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def update_me(user_id: int, request: Request, db: AsyncSession):
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
        
        user = await user_model.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_profile_update_request")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        user = await user_model.update_user_profile(db, user, nickname, profile_image)

        return JSONResponse(
            status_code=200,
            content={
                "detail": "profile_update_success",
                "data": {
                    "user_id": user.user_id,
                    "nickname": user.nickname,
                    "profile_image": getattr(user, "profile_image", None),
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[update-profile] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def update_password(user_id: int, request: Request, db: AsyncSession):
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
        
        user = await user_model.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_password_update_request")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        if not await utils.verify_password_async(current_password, user.password):
            raise HTTPException(status_code=400, detail="invalid_password")
        
        hashed_new_password = await utils.hash_password_async(new_password)

        await user_model.update_user_password(db, user, hashed_new_password)
        return JSONResponse(status_code=200, content={"detail": "password_update_success"})
    except HTTPException:
        raise
    except Exception as e:
        print("[update password] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def logout(user_id: int, request: Request, db: AsyncSession):
    try:
        if not await user_model.get_user_by_id(db, user_id):
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
    except Exception as e:
        print("[logout] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def delete_user(user_id: int, request: Request, db: AsyncSession):
    try:
        if not await user_model.get_user_by_id(db, user_id):
            raise HTTPException(status_code=400, detail="invalid_user_delete_request")
    
        session_email = request.session.get("email")
        session_id = request.session.get("sessionID")
        session_user_id = request.session.get("user_id")

        if not session_email or not session_id or not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        request.session.clear()
        
        await user_model.delete_user(db, user_id)
        return JSONResponse(status_code=200, content={"detail": "user_delete_success"})
    except HTTPException:
        raise
    except Exception as e:
        print("[delete-user] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")


async def upload_image (file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="invalid_image_upload_request")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="invalid_image_upload_request")
    try:
        PROJECT_ROOT = Path(__file__).resolve().parents[3]
        IMAGE_DIR = PROJECT_ROOT / "image"

        original_name = file.filename or ""
        ext = os.path.splitext(original_name)[1].lower()

        unique_name = f"{uuid.uuid4().hex}{ext}"
        save_path = IMAGE_DIR / unique_name

        with save_path.open("wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB씩
                if not chunk:
                    break
                buffer.write(chunk)

        public_path = f"/image/{unique_name}"
        base_url = "http://localhost:8000"
        public_path = base_url + public_path

        return JSONResponse(
            status_code=201,
            content={
                "detail": "image_upload_success",
                "data": {
                    "file_path": public_path
                },
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        print("[upload-image] unexpected error:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="internal_server_error")                 