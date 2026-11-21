from datetime import date as Date
from typing import Literal

from pydantic import BaseModel, Field


# ---------- 데이터(data) ----------
class DataIn(BaseModel):
    date: Date
    value: int = Field(..., ge=0, description="수치(예: 일별 매출, 원 단위)")
    memo: str = Field("", max_length=200)


class DataOut(BaseModel):
    id: str
    date: str
    value: int
    memo: str


# ---------- 요약(summary) ----------
class Metrics(BaseModel):
    total: int
    average: int
    max: int
    min: int


class Point(BaseModel):
    date: str
    value: int


class SummaryOut(BaseModel):
    period: str | None
    count: int
    metrics: Metrics | None
    trend: str
    latest: Point | None = None
    best: Point | None = None


# ---------- 대화(conversations) ----------
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ConversationIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    messages: list[Message] = Field(default_factory=list, max_length=200)


# ---------- 채팅(chat) ----------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
