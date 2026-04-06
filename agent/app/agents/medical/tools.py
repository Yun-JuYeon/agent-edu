"""의료 데이터 검색 도구"""

from langchain_core.tools import tool

from app.services.elasticsearch_service import ElasticsearchService
from app.utils.logger import custom_logger


@tool
def search_medical_data(query: str) -> str:
    """Elasticsearch에서 의료 데이터를 검색합니다.
    사용자의 질문과 관련된 의료 문서를 검색하여 반환합니다.
    의료 관련 질문에 답변하기 위해 이 도구를 사용하세요.

    Args:
        query: 검색할 의료 관련 질문 또는 키워드
    """
    try:
        es_service = ElasticsearchService()
        return es_service.search(query)
    except Exception as e:
        custom_logger.error(f"Elasticsearch 검색 오류: {e}")
        return f"검색 중 오류가 발생했습니다: {str(e)}"
