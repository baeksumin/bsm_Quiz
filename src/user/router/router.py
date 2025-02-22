from common.db.database import get_db  # DB 세션 의존성
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.user.schema.schema import TokenResponse, UserCreate, UserLogin
from src.user.service.service import authenticate_user, register_user

router = APIRouter()

@router.post(
    "/register"
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    ** 회원가입 API **
    - **새로운 사용자를 생성**합니다.  
    - `username`, `email`, `password` 필수 입력.  
    - 이메일은 중복될 수 없습니다.  
    - 비밀번호는 해시화되어 저장됩니다.  
    - 성공 시, 생성된 사용자 정보 반환.
    """
    return register_user(db, user_data)

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """  
    ** 로그인 API ** 
    - **등록된 사용자만 로그인 가능**합니다.  
    - `email`, `password` 입력.  
    - 비밀번호 검증 후 **JWT 토큰 발급.**  
    - 발급된 토큰은 API 호출 시 **인증 헤더에 포함하여 사용.**
    """
    return authenticate_user(db, login_data)

