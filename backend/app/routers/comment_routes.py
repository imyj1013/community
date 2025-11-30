from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..controllers import comment_controller as cc
from app.db import get_db

router = APIRouter()

@router.post("/comment")
async def create_comment(request: Request, db: AsyncSession = Depends(get_db)):
    return await cc.create_comment(request, db)

@router.put("/comment/{comment_id}")
async def update_comment(comment_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    return await cc.update_comment(comment_id, request, db)

@router.delete("/comment/{comment_id}")
async def delete_comment(comment_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    return await cc.delete_comment(comment_id, request, db)
