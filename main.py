from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
from routers import chat, conversations, data

app = FastAPI(
    title="내 상황을 아는 AI 비서 API",
    version="1.0.0",
    description="시계열 데이터 CRUD, 요약, 대화 기록, 컨텍스트 주입 채팅 API",
)

# 프론트엔드(Vercel) 도메인만 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
