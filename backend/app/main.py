from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from .routers.user_routes import router as user_router
from .routers.post_routes import router as post_router
from .routers.comment_routes import router as comment_router
from .routers.like_routes import router as like_router

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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_DIR = PROJECT_ROOT / "image"

IMAGE_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/image",
    StaticFiles(directory=IMAGE_DIR),
    name="image",
)