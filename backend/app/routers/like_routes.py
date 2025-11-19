from fastapi import APIRouter, Request
from app.controllers import like_controller as lc

router = APIRouter()

@router.post("/like")
async def create_like(request: Request):
    return await lc.create_like(request)

@router.delete("/like/{like_id}")
async def delete_like(like_id: int, request: Request):
    return await lc.delete_like(like_id, request)
