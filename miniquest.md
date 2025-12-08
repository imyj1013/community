# 미니퀘스트 정리
설치나 실습 관련 미니퀘스트는 프로젝트 코드 참고

## HTTP메서드, 상태코드에 대해서 각각 한 줄로 정리해보세요.

- **HTTP 메서드**  
  HTTP에서 클라이언트가 서버의 리소스에 대해 “무엇을 할지”를 나타내는 동사 역할의 명령으로, 대표적으로 GET(조회), POST(생성), PUT/PATCH(수정), DELETE(삭제) 등이 있다.

- **HTTP 상태 코드(Status Code)**  
  서버가 클라이언트의 요청을 어떻게 처리했는지를 세 자리 숫자로 나타내는 응답 코드로, 2xx(성공), 3xx(리다이렉션), 4xx(클라이언트 오류), 5xx(서버 오류) 등의 범주로 구분된다.

---

## JSONResponse를 공부하고 커스텀 상태 코드(Status Code) 설정, 커스텀 헤더(Header) 추가, 쿠키(Cookie) 설정 구현해 보세요.

### JSONResponse란?

- FastAPI는 기본적으로 `dict`나 `pydantic` 모델을 리턴하면 자동으로 JSON 응답을 만들어주지만,  
  `JSONResponse`를 사용하면 **응답 본문, 상태 코드, 헤더, 쿠키** 등을 직접 컨트롤할 수 있다.
- `from fastapi.responses import JSONResponse` 로 가져와서 사용한다.

### 예시 코드

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/custom-response")
def custom_response():
    # 응답 바디
    content = {
        "message": "커스텀 응답입니다.",
        "success": True
    }

    # JSONResponse 생성 + 커스텀 상태코드
    response = JSONResponse(
        content=content,
        status_code=201  # 201 Created
    )

    # 커스텀 헤더 추가
    response.headers["X-Custom-Header"] = "MyCustomValue"

    # 쿠키 설정(예: 세션 ID)
    response.set_cookie(
        key="session_id",
        value="abc123",
        httponly=True,   # JS에서 접근 불가 (보안)
        max_age=60 * 60  # 1시간
    )

    return response
````

* **커스텀 상태 코드**: `status_code=201` 처럼 직접 숫자를 넣어서 설정.
* **커스텀 헤더**: `response.headers["X-..."] = "..."` 형식으로 추가.
* **쿠키**: `set_cookie` 메서드를 사용해 키, 값, 옵션(httponly, 만료시간 등)을 설정.

---

## 타임아웃 미들웨어에 대해 공부하고 적용해보세요

### 타임아웃 미들웨어란?

* 클라이언트 요청이 **너무 오래 걸릴 때** 일정 시간 이상이 지나면 요청을 강제로 끊고
  **타임아웃 응답(보통 504 Gateway Timeout)** 을 보내주는 미들웨어이다.
* 서버가 무한 대기 상태에 빠지거나, 외부 API 호출이 오래 걸리는 상황에서
  서버 전체가 묶이지 않도록 보호하는 역할을 한다.

### 예시 코드 (간단한 TimeoutMiddleware)

```python
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout: int = 5):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        try:
            # 주어진 시간 안에 요청 처리 시도
            response = await asyncio.wait_for(call_next(request), timeout=self.timeout)
            return response
        except asyncio.TimeoutError:
            # 타임아웃 발생 시 504 응답
            return JSONResponse(
                status_code=504,
                content={"detail": f"Request timeout (>{self.timeout} seconds)"}
            )

# 미들웨어 등록
app.add_middleware(TimeoutMiddleware, timeout=5)

@app.get("/slow")
async def slow_api():
    # 일부러 오래 걸리는 API
    await asyncio.sleep(10)
    return {"message": "이 응답은 타임아웃 때문에 실제로는 도달하기 어려움"}
```

---

## rate-limit 미들웨어에 대해 공부하고 적용해보세요.

### 레이트 리밋(Rate Limit)란?

* 하나의 클라이언트(IP 등)가 **너무 많은 요청을 한 번에 보내는 것**을 막기 위해
  **일정 시간 동안 허용되는 요청 수를 제한하는 기능**이다.
* 예: “같은 IP에서 1분에 60번 이상 요청하면 429 Too Many Requests 응답 보내기”

### 인메모리 구현 예시

> 주의: 인메모리이므로 서버가 재시작되면 데이터가 초기화되며, 멀티 프로세스 환경에서는 공유되지 않는다.

```python
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

# 간단한 인메모리 저장소: { ip: { "count": int, "reset_time": float } }
rate_limit_store = {}

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()

        # 해당 IP 정보 가져오기
        data = rate_limit_store.get(client_ip)

        if data is None or now > data["reset_time"]:
            # 새 윈도우 시작
            rate_limit_store[client_ip] = {
                "count": 1,
                "reset_time": now + self.window_seconds
            }
        else:
            # 기존 윈도우 안
            if data["count"] >= self.limit:
                # 제한 초과
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too Many Requests",
                        "limit": self.limit,
                        "window_seconds": self.window_seconds
                    }
                )
            else:
                # 카운트 증가
                data["count"] += 1

        response = await call_next(request)
        return response

# 미들웨어 등록 (예: 60초에 5번까지 허용)
app.add_middleware(RateLimitMiddleware, limit=5, window_seconds=60)

@app.get("/limited")
def limited_endpoint():
    return {"message": "rate limit 안에서 정상 응답입니다."}
```

---

## CORSMiddleware에 대해서 공부하고 적용해 보세요.

### CORS란?

* **Cross-Origin Resource Sharing**의 약자로,
  브라우저에서 “다른 도메인/포트/프로토콜(origin)”에 있는 리소스에 요청을 보낼 때 **보안을 위해 적용되는 규칙**이다.
* 기본적으로 브라우저는 서로 다른 origin 간 요청을 제한하고,
  서버에서 `Access-Control-*` 헤더를 통해 허용 범위를 명시해야 한다.

### CORSMiddleware 적용 예시

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 허용할 origin 목록
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://my-frontend.example.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # 어떤 Origin을 허용할지
    allow_credentials=True,         # 쿠키/인증 정보 허용 여부
    allow_methods=["*"],            # 허용할 HTTP 메서드
    allow_headers=["*"],            # 허용할 HTTP 헤더
)

@app.get("/cors-test")
def cors_test():
    return {"message": "CORS 설정이 적용된 엔드포인트입니다."}
```

---

## dot.env에 대해 공부하고 적용해보세요

### .env (dotenv)란?

* `.env` 파일은 **환경 변수(environment variables)** 를 저장하는 텍스트 파일이다.
* DB 비밀번호, 시크릿 키, API 토큰 등 **민감한 정보를 코드에 직접 쓰지 않고**
  `.env` 파일에 분리해 두고, 실행 시점에 환경 변수로 불러와서 사용한다.
* 일반적으로 `.env` 파일은 **Git에 올리지 않고(.gitignore)** 로컬/서버 환경마다 따로 관리한다.

#### 예시 `.env` 파일

```env
SECRET_KEY=super-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
DEBUG=True
```

#### FastAPI에서 사용하는 예시 (python-dotenv)

```python
# app/config.py
import os
from dotenv import load_dotenv

# .env 파일 읽기
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = os.getenv("DEBUG", "False") == "True"
```

```python
# app/main.py
from fastapi import FastAPI
from app.config import SECRET_KEY, DEBUG

app = FastAPI(
    title="Env Example",
    debug=DEBUG
)

@app.get("/env-check")
def env_check():
    return {
        "secret_key_loaded": SECRET_KEY is not None,
        "debug": DEBUG
    }
```

* 실제 서비스에서는 pydantic의 `BaseSettings` 를 활용한 설정 클래스(`Settings`) 패턴도 자주 사용한다.

---

## 웹 스토리지(Web Storage)에 대해 정리해보세요

**웹 스토리지(Web Storage)** 는 브라우저에 데이터를 저장하기 위한 기능으로,
대표적으로 `localStorage` 와 `sessionStorage` 두 가지가 있다. (쿠키와는 별도)

### 공통 특징

* 문자열 형태로 key-value 데이터를 저장한다.
* HTTP 요청마다 자동으로 전송되지 않으므로, **쿠키보다 용량이 크고 네트워크 부담이 적다.**
* JavaScript에서 `window.localStorage`, `window.sessionStorage` 로 접근한다.

### 1) localStorage

* **브라우저를 닫아도 데이터가 유지**되는 저장소.
* 같은 도메인(origin)에서는 새로고침/브라우저 재시작 후에도 그대로 남아 있다.
* 용량이 쿠키보다 훨씬 크고, 장기적인 설정값, 토큰(보안 이슈 주의) 등을 저장할 때 사용한다.

```javascript
// 저장
localStorage.setItem("theme", "dark");

// 조회
const theme = localStorage.getItem("theme");

// 삭제
localStorage.removeItem("theme");

// 전체 삭제
localStorage.clear();
```

### 2) sessionStorage

* **브라우저 탭(세션)이 유지되는 동안만** 저장되는 저장소.
* 같은 사이트라도 **다른 탭은 다른 sessionStorage** 를 가진다.
* 탭을 닫으면 해당 sessionStorage 데이터는 사라진다.

```javascript
// 저장
sessionStorage.setItem("tempToken", "12345");

// 조회
const token = sessionStorage.getItem("tempToken");

// 삭제
sessionStorage.removeItem("tempToken");

// 전체 삭제
sessionStorage.clear();
```

### 쿠키와의 차이 (간단 비교)

* **쿠키(Cookie)**

  * 서버가 `Set-Cookie` 헤더로 내려주고 브라우저가 관리.
  * 만료 시간, Domain, Path 등을 설정 가능.
  * 기본적으로 같은 도메인의 HTTP 요청마다 자동으로 전송됨 → 인증/세션 관리에 자주 사용.
  * 용량이 작고, 너무 많이 사용하면 요청마다 전송되어 성능에 영향.

* **웹 스토리지(localStorage / sessionStorage)**

  * 오직 브라우저에서만 읽고 쓰며, HTTP 요청에 자동으로 포함되지 않는다.
  * 비교적 용량이 크고, JSON 문자열 등을 저장하기 좋다.
  * 보안 상 민감한 값(JWT 등)을 저장할 때는 XSS 취약점이 없는지 매우 주의해야 한다.

