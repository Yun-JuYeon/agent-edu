"""대화 스레드 관리 API"""

import uuid
from fastapi import APIRouter, HTTPException

from app.services.thread_store import thread_store

threads_router = APIRouter()


@threads_router.get("/favorites/questions")
async def get_favorite_questions():
    """즐겨찾기된 질문 목록 (현재 미구현 - 빈 목록 반환)"""
    return {"response": []}


@threads_router.get("/threads")
async def get_all_threads():
    """대화 스레드 목록 조회"""
    return {"response": thread_store.list_threads()}


@threads_router.get("/threads/{thread_id}")
async def get_thread_by_id(thread_id: uuid.UUID):
    """특정 스레드의 메시지 내역 조회"""
    thread = thread_store.get_thread(str(thread_id))
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"response": thread}


@threads_router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: uuid.UUID):
    """스레드 삭제"""
    if not thread_store.delete_thread(str(thread_id)):
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"success": True}
