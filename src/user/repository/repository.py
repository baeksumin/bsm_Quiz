from sqlalchemy.orm import Session
from src.user.model import User
from src.user.schema.schema import UserCreate
from passlib.context import CryptContext
from datetime import datetime
import pytz

KST = pytz.timezone("Asia/Seoul")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user_data: UserCreate):
    hashed_password = pwd_context.hash(user_data.password)
    db_user = User(
        username=user_data.username, 
        email=user_data.email, 
        password_hash=hashed_password, 
        is_admin=user_data.is_admin,
        created_at=datetime.now(KST),
        updated_at=datetime.now(KST))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
