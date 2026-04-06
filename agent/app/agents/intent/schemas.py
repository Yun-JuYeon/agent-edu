"""Intent 분류 결과 스키마"""

from typing import Literal
from pydantic import BaseModel, Field


class IntentClassification(BaseModel):
    """사용자 메시지의 intent 분류 결과"""

    intent: Literal["MEDICAL", "GENERAL"] = Field(
        description=(
            "MEDICAL: 질병, 증상, 치료, 약물 등 의료 관련 질문. "
            "GENERAL: 인사, 잡담, 감사 등 일반 대화."
        )
    )
