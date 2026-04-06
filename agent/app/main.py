from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes.threads import threads_router
from app.api.routes.chat import chat_router
from app.api.middleware import LoggingMiddleware

app = FastAPI(
    title="Medical Agent",
    description="LangChain 기반 의료 Q&A 에이전트",
    version="0.1.0",
)

api_router = APIRouter(prefix=settings.API_V1_PREFIX)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP 로깅 미들웨어
app.add_middleware(LoggingMiddleware)

# API 라우터 등록
api_router.include_router(threads_router, tags=["threads"])
api_router.include_router(chat_router, tags=["chat"])
app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Medical Agent API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
