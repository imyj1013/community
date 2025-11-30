import re
from passlib.context import CryptContext
from fastapi.concurrency import run_in_threadpool

def email_is_valid(email: str):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def nickname_is_valid(nickname: str):
    pattern = r'^\S{1,10}$'
    return re.match(pattern, nickname) is not None

def format_number(n: int) -> str:
    if n >= 100_000:
        return f"{n // 1000}k"
    elif n >= 10_000:
        return f"{n // 1000}k"
    elif n >= 1_000:
        return f"{n // 1000}k"
    else:
        return str(n)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

async def hash_password_async(password: str) -> str:
    return await run_in_threadpool(pwd_context.hash, password)

async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    return await run_in_threadpool(pwd_context.verify, plain_password, hashed_password)