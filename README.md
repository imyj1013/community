# **Community Web Service (FastAPI + MySQL + Vanilla JS)**

이 프로젝트는 **FastAPI + MySQL + Vanilla JavaScript** 기반으로 구현된 풀스택 커뮤니티 서비스입니다.
사용자는 회원가입·로그인, 게시글 작성 및 자동 요약, 댓글·좋아요 기능, 프로필 관리 등을 수행할 수 있으며
AI 모델(BART)을 활용한 게시글 요약 기능과 이미지 업로드 시스템도 포함되어 있습니다.

---

# **주요 기능 요약**

### 사용자 기능

* 회원가입 / 로그인 / 로그아웃 (세션 기반 인증)
* 이메일 / 닉네임 중복 검사
* 프로필 수정 (닉네임 + 프로필 이미지)
* 비밀번호 변경
* 회원 탈퇴 (CASCADE로 관련 데이터 모두 삭제)

### 게시글 기능

* 게시글 작성 / 수정 / 삭제
* **AI 요약 자동 생성 (BART 모델 활용)**
* 이미지 업로드 및 기존 이미지 삭제 기능
* 무한 스크롤 기반 게시글 목록
* 상세보기 / 조회수 증가

### 댓글 기능

* 댓글 작성 / 수정 / 삭제
* 본인 댓글 여부는 **user_id 기반**으로 검증
* 댓글 작성자 프로필 이미지 표시

### 좋아요 기능

* 좋아요 등록 / 취소
* 게시글별 좋아요 수 표시
* 사용자별 좋아요 여부 체크

### 이미지 업로드

* FastAPI UploadFile → StaticFiles 제공
* `/image/<uuid>.png` 형태로 반환
* 프론트에서 자동 미리보기 / 삭제 가능

---

# **실행 방법**

## 1. Backend 실행

### ▶ 가상환경 생성 및 패키지 설치

```bash
conda create -n env_community python=3.10
conda activate env_community
pip install -r backend/requirements.txt
```

### ▶ MySQL 준비

MySQL 실행 후 `db.py`에 본인의 환경에 맞게 정보 수정.

### ▶ 테이블 생성

```bash
cd backend
python create_table.py
```

### ▶ 모델 다운로드

```bash
cd backend
python download_model.py
```

### ▶ 서버 실행

```bash
uvicorn app.main:app --reload
```

서버 URL:

```
http://localhost:8000
```

API 문서:

```
http://localhost:8000/docs
http://localhost:8000/redoc
```

---

## 2. Frontend 실행

Frontend는 정적 파일이므로 내장 서버만 있으면 실행가능.

```bash
cd frontend
python -m http.server 5500
```

브라우저에서 접속:

```
http://localhost:5500/login.html
```

---

# **전체 동작 흐름 (Architecture Overview)**

1. **사용자 요청 → 프론트엔드 JS**

   * 모든 요청은 `fetch` + `credentials: "include"` 로 세션 유지
   * DOM 변경을 통해 실시간 UI 업데이트

2. **FastAPI 라우터 → 컨트롤러 → 모델 계층**

   * route: URL 엔드포인트 정의
   * controller: 비즈니스 로직 수행
   * model: 실제 DB CRUD 처리

3. **MySQL 데이터베이스**

   * CASCADE 설정으로 참조 데이터 자동 삭제
   * post, comment, like, user 간 연관관계 명확

4. **Static image 파일 제공**

   * `/image/<uuid>.png` 형태의 URL을 프론트가 받아서 렌더링

5. **AI 요약 모델(BART)**

   * 게시글 작성 시 본문을 기반으로 summary 자동 생성
   * tokenizer 입력 길이를 초과하면 truncation하여 안정성 확보

---

# **AI 요약 기능 상세 설명**

게시글 작성 시:

```
content → tokenizer → BART → generate(summary_ids)
```
---

# **시연영상**

https://drive.google.com/file/d/16yCrMHfZRHSoyG99GfKu6IIlS5KXJN1I/view?usp=sharing 
