from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from ..controllers import like_controller as lc
from app.db import get_db

router = APIRouter()

@router.post("/like")
async def create_like(request: Request, db: Session = Depends(get_db)):
    return await lc.create_like(request)

@router.delete("/like/{like_id}")
async def delete_like(like_id: int, request: Request, db: Session = Depends(get_db)):
    return await lc.delete_like(like_id, request)
