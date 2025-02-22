-- 사용자 테이블
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,   -- 사용자 이름
    email VARCHAR(255) UNIQUE NOT NULL,      -- 사용자 이메일
    password_hash VARCHAR(255) NOT NULL,     -- 비밀번호 해시
    is_admin BOOLEAN DEFAULT FALSE, -- 관리자 여부
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 생성일시
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 수정일시
);

-- 퀴즈 테이블
CREATE TABLE quiz (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,    -- 퀴즈 제목
    description TEXT,               -- 퀴즈 설명
    is_random_questions BOOLEAN DEFAULT FALSE, -- 문제 랜덤 여부
    is_random_choices BOOLEAN DEFAULT FALSE, -- 선택지 랜덤 여부
    questions_per_page INT DEFAULT 10, -- 한 페이지 당 문제 개수
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 생성일시
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 수정일시
);

-- 문제 테이블
CREATE TABLE question (
    id SERIAL PRIMARY KEY,
    quiz_id INT REFERENCES quiz(id) ON DELETE CASCADE, -- 퀴즈와 연결
    question_text TEXT NOT NULL,  -- 문제 내용
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 생성일시
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 수정일시
);

-- 선택지 테이블
CREATE TABLE choice (
    id SERIAL PRIMARY KEY,
    question_id INT REFERENCES question(id) ON DELETE CASCADE, -- 문제와 연결
    choice_text TEXT NOT NULL,     -- 선택지 내용
    is_correct BOOLEAN DEFAULT FALSE, -- 정답 여부
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 생성일시
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 수정일시
);

-- 퀴즈 응시 기록 테이블
CREATE TABLE quiz_record (
    id SERIAL PRIMARY KEY,
    quiz_id INT REFERENCES quiz(id) ON DELETE CASCADE, -- 퀴즈와 연결
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE, -- 사용자와 연결
    score INT DEFAULT 0,           -- 최종 점수
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 생성일시
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 수정일시
);

-- 사용자의 답안 정보 테이블
CREATE TABLE answer (
    id SERIAL PRIMARY KEY,
    quiz_record_id INT REFERENCES quiz_record(id) ON DELETE CASCADE, -- 응시 기록과 연결
    question_id INT REFERENCES question(id) ON DELETE CASCADE, -- 문제와 연결
    choice_id INT REFERENCES choice(id) ON DELETE CASCADE, -- 선택지와 연결
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 생성일시
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 수정일시
);
