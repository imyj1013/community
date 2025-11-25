from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from ..controllers import post_controller as pc
from app.db import get_db

router = APIRouter()

@router.get("/posts")
async def list_posts(cursor_id: int, count: int, db: Session = Depends(get_db)):
    return await pc.list_posts(cursor_id, count)

@router.post("/posts")
async def create_post(request: Request, db: Session = Depends(get_db)):
    return await pc.create_post(request)

@router.put("/posts/{post_id}")
async def update_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    return await pc.update_post(post_id, request)

@router.get("/posts/{post_id}")
async def get_post_detail(post_id: int, request: Request, db: Session = Depends(get_db)):
    return await pc.get_post_detail(post_id, request)

@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    return await pc.delete_post(post_id, request)
