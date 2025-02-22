from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security.oauth2 import OAuth2PasswordBearer

from src.quiz.router.router import router as quiz_router
from src.quiz.router.user_router import router as quiz_user_router
from src.user.router.router import router as user_router

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def custom_openapi():
    """Swagger에서 Bearer 토큰만 입력하도록 보이게 하는 설정"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="bsm_Quiz API",
        version="1.0.0",
        description="FastAPI Quiz",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if path.startswith("/quiz"):
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(quiz_router, prefix="/quiz", tags=["[관리자용] quiz"]) 
app.include_router(quiz_user_router, prefix="/quiz/user", tags=["[사용자용] quiz-user"]) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
