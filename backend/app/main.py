from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.routers.user_routes import router as user_router
from app.routers.post_routes import router as post_router
from app.routers.comment_routes import router as comment_router
from app.routers.like_routes import router as like_router

app = FastAPI(title="Community API - Route/Controller")

app.add_middleware(
    SessionMiddleware,
    secret_key="yourSecretKey",
    max_age=24 * 60 * 60,
    same_site="lax",
    https_only=False,
)

app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(like_router)
