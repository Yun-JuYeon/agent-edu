"""LangChain 기반 에이전트 팩토리"""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from app.core.config import settings
from app.agents.prompts import MEDICAL_SYSTEM_PROMPT
from app.agents.medical import search_medical_data
from app.agents.intent import intent_middleware


def create_medical_agent():
    """Elasticsearch 의료 데이터를 활용하는 LangChain 에이전트를 생성합니다."""

    model = init_chat_model(
        f"openai:{settings.OPENAI_MODEL}",
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )

    agent = create_agent(
        model=model,
        tools=[search_medical_data],
        system_prompt=MEDICAL_SYSTEM_PROMPT,
        middleware=[intent_middleware],
        checkpointer=InMemorySaver(),
        name="medical_agent",
    )

    return agent
