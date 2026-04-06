from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API
    API_V1_PREFIX: str
    CORS_ORIGINS: List[str] = ["*"]

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    INTENT_CLASSIFIER_MODEL: str = "gpt-4o-mini"

    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "medical_data"
    ELASTICSEARCH_USERNAME: str = ""
    ELASTICSEARCH_PASSWORD: str = ""

    # LangGraph 재귀 호출 한도
    AGENT_RECURSION_LIMIT: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
