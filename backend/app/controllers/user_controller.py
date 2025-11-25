from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
from . import __init__ as _
from .. import utils
from ..models import user_model

async def login(request: Request, db: Session):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_login_request")
    try:
        email = body.get("email")
        password = body.get("password")

        if not email or not password:
            raise HTTPException(status_code=400, detail="invalid_login_request")

        user = user_model.get_user_by_email(db, email)
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
        

async def signup(request: Request, db: Session):
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

        if user_model.get_user_by_email(db, email):
            raise HTTPException(status_code=400, detail="invalid_signup_request")

        user = user_model.create_user(db, email, password, nickname, profile_image)

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


async def check_email(email: str, db: Session):
    try:
        valid = utils.email_is_valid(email)
        if valid == True:
            exists = user_model.get_user_by_email(db, email) is not None
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


async def check_nickname(nickname: str, db: Session):
    try:
        valid = utils.nickname_is_valid(nickname)
        if valid == True:
            exists = user_model.get_user_by_nickname(db, nickname) is not None
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


async def update_me(user_id: int, request: Request, db: Session):
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
        
        user = user_model.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_profile_update_request")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")

        user = user_model.update_user_profile(db, user, nickname, profile_image)

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


async def update_password(user_id: int, request: Request, db: Session):
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
        
        user = user_model.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=400, detail="invalid_password_update_request")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        if user["password"] != current_password:
            raise HTTPException(status_code=400, detail="invalid_password")

        user = user_model.update_user_password(db, user, new_password)
        return JSONResponse(status_code=200, content={"detail": "password_update_success"})
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")


async def logout(user_id: int, request: Request, db: Session):
    try:
        if not user_model.get_user_by_id(db, user_id):
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


async def delete_user(user_id: int, request: Request, db: Session):
    try:
        if not user_model.get_user_by_id(db, user_id):
            raise HTTPException(status_code=400, detail="invalid_user_delete_request")
    
        session_email = request.session.get("email")
        session_id = request.session.get("sessionID")
        session_user_id = request.session.get("user_id")

        if not session_email or not session_id or not session_user_id:
            raise HTTPException(status_code=401, detail="unauthorized_user")
        
        if user_id != session_user_id:
            raise HTTPException(status_code=403, detail="forbidden_user")
        
        request.session.clear()
        
        user_model.delete_user(db, user_id)
        return JSONResponse(status_code=200, content={"detail": "user_delete_success"})
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="internal_server_error")

