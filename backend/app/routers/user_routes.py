from fastapi import APIRouter, Request, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from ..controllers import user_controller as uc
from app.db import get_db

router = APIRouter()

@router.post("/user/login")
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    return await uc.login(request, db)

@router.post("/user/signup")
async def signup(request: Request, db: AsyncSession = Depends(get_db)):
    return await uc.signup(request, db)

@router.get("/user/check-email")
async def check_email(email: str, db: AsyncSession = Depends(get_db)):
    return await uc.check_email(email, db)

@router.get("/user/check-nickname")
async def check_nickname(nickname: str, db: AsyncSession = Depends(get_db)):
    return await uc.check_nickname(nickname, db)

@router.put("/user/update-me/{user_id}")
async def update_me(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    return await uc.update_me(user_id, request, db)

@router.put("/user/update-password/{user_id}")
async def update_password(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    return await uc.update_password(user_id, request, db)

@router.delete("/user/logout/{user_id}")
async def logout(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    return await uc.logout(user_id, request, db)

@router.delete("/user/{user_id}")
async def delete_user(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    return await uc.delete_user(user_id, request, db)

@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    return await uc.upload_image(file)