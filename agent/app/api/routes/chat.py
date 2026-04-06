"""채팅 SSE 스트리밍 API"""

import json
import uuid
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest
from app.services.agent_service import AgentService
from app.services.thread_store import thread_store
from app.utils.logger import custom_logger

chat_router = APIRouter()


@chat_router.post("/chat")
async def post_chat(request: ChatRequest):
    """자연어 쿼리를 에이전트가 처리하고 SSE로 스트리밍합니다."""
    custom_logger.info(f"Chat 요청: thread={request.thread_id}, msg={request.message[:50]}")
    thread_id = str(request.thread_id)

    # 사용자 메시지 즉시 저장 (필요 시 새 스레드 자동 생성)
    thread_store.add_user_message(thread_id, request.message)

    async def event_generator():
        agent_service = AgentService()
        final_payload: dict | None = None

        try:
            async for chunk in agent_service.process_query(
                user_messages=request.message,
                thread_id=request.thread_id,
            ):
                # 마지막 done payload를 잡아서 store에 저장
                try:
                    parsed = json.loads(chunk)
                    if parsed.get("step") == "done" and not parsed.get("error"):
                        final_payload = parsed
                except (json.JSONDecodeError, TypeError):
                    pass

                yield f"data: {chunk}\n\n"

        except Exception as e:
            custom_logger.error(f"event_generator 오류: {e}")
            error_response = {
                "step": "done",
                "message_id": str(uuid.uuid4()),
                "role": "assistant",
                "content": "요청 처리 중 오류가 발생했습니다. 다시 시도해주세요.",
                "metadata": {},
                "created_at": datetime.utcnow().isoformat(),
                "error": str(e),
            }
            yield f"data: {json.dumps(error_response, ensure_ascii=False)}\n\n"
            return

        # 스트리밍 종료 후 최종 응답을 store에 저장
        if final_payload:
            thread_store.add_assistant_message(
                thread_id=thread_id,
                content=final_payload.get("content", ""),
                message_id=final_payload.get("message_id"),
                metadata=final_payload.get("metadata"),
            )

    return StreamingResponse(event_generator(), media_type="text/event-stream")
