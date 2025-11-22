from fastapi import APIRouter, Request
from app.controllers import comment_controller as cc

router = APIRouter()

@router.post("/comment")
async def create_comment(request: Request):
    return await cc.create_comment(request)

@router.put("/comment/{comment_id}")
async def update_comment(comment_id: int, request: Request):
    return await cc.update_comment(comment_id, request)

@router.delete("/comment/{comment_id}")
async def delete_comment(comment_id: int, request: Request):
    return await cc.delete_comment(comment_id, request)
