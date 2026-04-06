"""Intent 분류 미들웨어 — 일반 대화는 도구 호출 없이 바로 응답"""

from langchain.agents.middleware import wrap_model_call, ModelRequest
from langchain_core.messages import HumanMessage

from app.utils.logger import custom_logger
from app.agents.intent.classifier import classify_intent


def _extract_last_user_text(messages) -> str:
    """메시지 리스트에서 가장 최근 user 메시지의 텍스트를 반환합니다."""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage) or getattr(msg, "type", None) == "human":
            return getattr(msg, "content", "") or ""
    return ""


@wrap_model_call
async def intent_middleware(request: ModelRequest, handler):
    """첫 번째 모델 호출 전에 intent를 판별. GENERAL이면 도구를 제거합니다."""
    user_text = _extract_last_user_text(request.messages)
    if not user_text:
        return await handler(request)

    result = await classify_intent(user_text)
    custom_logger.info(f"[Intent] '{user_text[:30]}...' → {result.intent}")

    if result.intent == "GENERAL":
        return await handler(request.override(tools=[]))

    return await handler(request)
