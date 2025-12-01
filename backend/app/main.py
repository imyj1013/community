import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .routers.user_routes import router as user_router
from .routers.post_routes import router as post_router
from .routers.comment_routes import router as comment_router
from .routers.like_routes import router as like_router
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SESSION_SECRET_KEY")

app = FastAPI(title="Community API")

origins = [
    "http://localhost:5500",   # 아래에서 띄울 프론트 서버
    "http://127.0.0.1:5500",
    "null",                    # file:// 로 테스트할 때(임시)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
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