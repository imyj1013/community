from fastapi import APIRouter, Request
from app.controllers import user_controller as uc

router = APIRouter()

@router.post("/user/login")
async def login(request: Request):
    return await uc.login(request)

@router.post("/user/signup")
async def signup(request: Request):
    return await uc.signup(request)

@router.get("/user/check-email")
async def check_email(email: str):
    return await uc.check_email(email)

@router.get("/user/check-nickname")
async def check_nickname(nickname: str):
    return await uc.check_nickname(nickname)

@router.put("/user/update-me/{user_id}")
async def update_me(user_id: int, request: Request):
    return await uc.update_me(user_id, request)

@router.put("/user/update-password/{user_id}")
async def update_password(user_id: int, request: Request):
    return await uc.update_password(user_id, request)

@router.delete("/user/logout/{user_id}")
async def logout(user_id: int, request: Request):
    return await uc.logout(user_id, request)

@router.delete("/user/{user_id}")
async def delete_user(user_id: int, request: Request):
    return await uc.delete_user(user_id, request)
