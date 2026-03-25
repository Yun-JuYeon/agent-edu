"""LangGraph 기반 의료 Q&A 에이전트"""

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.agents.prompts import system_prompt
from app.agents.tools import search_medical_data


def create_medical_agent():
    """Elasticsearch 의료 데이터를 활용하는 LangGraph ReAct 에이전트를 생성합니다."""

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
        streaming=True,
    )

    tools = [search_medical_data]
    memory = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        prompt=system_prompt,
    )

    return agent
