# 백수민_quiz

이 프로젝트는 **FastAPI**와 **PostgreSQL**을 기반으로 한 **퀴즈 응시 시스템**입니다. 관리자(Admin)가 퀴즈(시험지)를 생성/관리하고, 사용자는 퀴즈를 응시하여 자동 채점을 받을 수 있습니다.

## 주요 기능

### 1. 회원가입 & 로그인 (JWT 인증)
- `POST /user/register` → 회원가입
- `POST /user/login` → 로그인 시 JWT 토큰 발급

### 2. 관리자용 퀴즈 API
- `POST /quiz/create` → 퀴즈 생성 (문제는 별도 등록)
- `PUT /quiz/{quiz_id}/questions` → 기존 퀴즈에 문제 추가
- `GET /quiz/list` → 퀴즈 목록 조회 (페이지네이션)
- `GET /quiz/{quiz_id}` → 퀴즈 상세 조회
- `PATCH /quiz/{quiz_id}/settings` → 문제/선택지 랜덤 여부, 페이지당 문항 수 설정

### 3. 사용자용 퀴즈 API
- `GET /quiz/user/list?completed=true/false` → 응시한 퀴즈 / 응시하지 않은 퀴즈 조회
- `GET /quiz/user/{quiz_id}` → 퀴즈 상세 (문제 & 선택지) 조회 (정답 미포함)
- `POST /quiz/user/{quiz_id}/attempt` → 퀴즈 응시 시작 (응시 기록 생성)
- `POST /quiz/user/{quiz_id}/attempt/{attempt_id}/submit` → 답안 제출 & 자동 채점
- `GET /quiz/user/attempt/{attempt_id}` → 응시 기록 조회 (점수, 제출 답안 등)

##  DB 세팅 (PostgreSQL)

### 1. PostgreSQL 설치
- Mac: `brew install postgresql`
- Linux(Ubuntu): `sudo apt-get install postgresql`
- Windows: [PostgreSQL 공식 사이트](https://www.postgresql.org/download/)

### 2. DB 생성
```bash
psql -U postgres
CREATE DATABASE quiz_db;
```

### 3. 유저 생성 & 권한 부여
```sql
CREATE USER quiz_user WITH PASSWORD password;
GRANT ALL PRIVILEGES ON DATABASE quiz_db TO quiz_user;
```

### 4. schema.sql 적용
```bash
psql -U quiz_user -d quiz_db < ./common/db/schema.sql
```
- `schema.sql` 파일의 내용을 DB에 적용해 테이블 생성
- 이후 `SELECT * FROM quiz_record;` 등으로 테이블이 잘 만들어졌는지 확인

## 실행 방법

### 1. 가상환경 설정
```bash
python3 -m venv venv
source venv/bin/activate # (Windows: venv\Scripts\activate)
```

### 2. 필수 라이브러리 설치
```bash
pip install -r requirements.txt
```


### 3. 서버 실행
```bash
uvicorn src.main:app --reload
```
- 서버가 `http://127.0.0.1:8000` 에서 동작
- Swagger 문서: `http://127.0.0.1:8000/docs`
- ReDoc 문서: `http://127.0.0.1:8000/redoc`

## 참고 사항

### JWT 인증
- 로그인 후 발급받은 `access_token`을 `Authorization: Bearer <token>` 형태로 요청 헤더에 포함해야 인증됨.

### 관리자 권한
- `user` 테이블의 `is_admin = TRUE` 인 유저만 퀴즈 생성/수정 API를 호출할 수 있음.

### 문항 및 선택지 랜덤 배치
- `is_random_questions`, `is_random_choices` 값에 따라 사용자 조회 시 각각 랜덤으로 배치 가능.

### 자동 채점 로직
- 기본적으로 `(정답 개수 / 전체 문제 수) * 100` 방식으로 점수 계산 (코드 내 수정 가능).