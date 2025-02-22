from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

SECRET_KEY = "3f9dbf1a0a921f713ef57cac46ce3653cf9a0c88a6233d20817c99de2f8c0a3e"  # 실제로는 .env 등에서 관리
ALGORITHM = "HS256"

class JWTBearer(HTTPBearer):
    """HTTP Bearer 헤더에서 JWT 토큰을 추출하고 검증하는 클래스"""
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if credentials.scheme.lower() == "bearer":
                token = credentials.credentials
                if not self.verify_jwt(token):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Invalid or expired token."
                    )
                return token
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code."
            )

    def verify_jwt(self, token: str) -> bool:
        """JWT가 유효한지 검증"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # payload에서 user_id 등을 가져와서 추가 검증도 가능
        except JWTError:
            return False
        return True

def get_current_user(token: str = Depends(JWTBearer())):
    """토큰에서 사용자 정보 추출"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 여기서 user_id 꺼내 DB 조회 후 유저 객체 반환도 가능
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or has expired")

def get_current_admin(current_user: dict = Depends(get_current_user)):
    """관리자 권한이 있는지 확인"""
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user