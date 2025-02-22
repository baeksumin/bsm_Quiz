from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import pytz

KST = pytz.timezone("Asia/Seoul")

# JWT 설정값
SECRET_KEY = "3f9dbf1a0a921f713ef57cac46ce3653cf9a0c88a6233d20817c99de2f8c0a3e"  # 실제 운영 환경에서는 .env 파일에서 불러와야 함 (openssl rand -hex 32 사용하여 생성)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720  # 12시간, 실제 운영 환경에서는 시간을 더 짧게 함

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.now(KST) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
