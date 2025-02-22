from util.security import create_access_token
from sqlalchemy.orm import Session
from src.user.repository.repository import create_user, get_user_by_email
from src.user.schema.schema import TokenResponse, UserCreate, UserLogin, UserResponse
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def register_user(db: Session, user_data: UserCreate) -> UserResponse:
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = create_user(db, user_data)
    return UserResponse(id=new_user.id, username=new_user.username, email=new_user.email)

def authenticate_user(db: Session, login_data: UserLogin) -> TokenResponse:
    """사용자 인증 후 JWT 토큰 발급"""
    user = get_user_by_email(db, login_data.email)
    if not user or not pwd_context.verify(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id, "is_admin": user.is_admin})
    
    return TokenResponse(access_token=access_token, token_type="bearer")
