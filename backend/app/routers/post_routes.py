from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..controllers import post_controller as pc
from app.db import get_db

router = APIRouter()

@router.get("/posts")
async def list_posts(cursor_id: int, count: int, db: AsyncSession = Depends(get_db)):
    return await pc.list_posts(cursor_id, count, db)

@router.post("/posts")
async def create_post(request: Request, db: AsyncSession = Depends(get_db)):
    return await pc.create_post(request, db)

@router.put("/posts/{post_id}")
async def update_post(post_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    return await pc.update_post(post_id, request, db)

@router.get("/posts/{post_id}")
async def get_post_detail(post_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    return await pc.get_post_detail(post_id, request, db)

@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    return await pc.delete_post(post_id, request, db)
