"""Chat API 요청/응답 모델 정의"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID


class ChatRequest(BaseModel):
    thread_id: UUID
    message: str


class ChatResponse(BaseModel):
    message_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
