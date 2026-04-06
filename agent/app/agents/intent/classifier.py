"""LLM 기반 Intent 분류기 (structured output)"""

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config import settings
from app.agents.prompts import INTENT_CLASSIFIER_PROMPT
from app.agents.intent.schemas import IntentClassification


# 분류 전용 경량 모델 (싱글톤)
_classifier = None


def _get_classifier():
    """structured output이 바인딩된 분류기 인스턴스를 반환합니다."""
    global _classifier
    if _classifier is None:
        model = init_chat_model(
            f"openai:{settings.INTENT_CLASSIFIER_MODEL}",
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )
        _classifier = model.with_structured_output(IntentClassification)
    return _classifier


async def classify_intent(user_text: str) -> IntentClassification:
    """사용자 메시지의 intent를 분류합니다."""
    classifier = _get_classifier()
    return await classifier.ainvoke([
        SystemMessage(content=INTENT_CLASSIFIER_PROMPT),
        HumanMessage(content=user_text),
    ])
