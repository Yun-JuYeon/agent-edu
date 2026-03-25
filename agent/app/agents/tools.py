"""Elasticsearch 기반 의료 데이터 검색 도구 정의"""

from langchain_core.tools import tool
from elasticsearch import Elasticsearch

from app.core.config import settings
from app.utils.logger import custom_logger


def _get_es_client() -> Elasticsearch:
    """Elasticsearch 클라이언트 생성"""
    kwargs = {
        "hosts": [settings.ELASTICSEARCH_URL],
    }
    if settings.ELASTICSEARCH_USERNAME and settings.ELASTICSEARCH_PASSWORD:
        kwargs["basic_auth"] = (
            settings.ELASTICSEARCH_USERNAME,
            settings.ELASTICSEARCH_PASSWORD,
        )
    return Elasticsearch(**kwargs)


@tool
def search_medical_data(query: str) -> str:
    """Elasticsearch에서 의료 데이터를 검색합니다.
    사용자의 질문과 관련된 의료 문서를 검색하여 반환합니다.
    의료 관련 질문에 답변하기 위해 이 도구를 사용하세요.

    Args:
        query: 검색할 의료 관련 질문 또는 키워드
    """
    try:
        es = _get_es_client()
        index = settings.ELASTICSEARCH_INDEX

        # multi_match 쿼리로 여러 필드에서 검색
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["*"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            },
            "size": 5,
        }

        response = es.search(index=index, body=search_body)
        hits = response.get("hits", {}).get("hits", [])

        if not hits:
            return f"'{query}'에 대한 검색 결과가 없습니다."

        results = []
        for i, hit in enumerate(hits, 1):
            source = hit.get("_source", {})
            score = hit.get("_score", 0)
            # 모든 필드를 텍스트로 변환
            fields_text = "\n".join(
                f"  - {k}: {v}" for k, v in source.items() if v
            )
            results.append(f"[결과 {i}] (관련도: {score:.2f})\n{fields_text}")

        return "\n\n".join(results)

    except Exception as e:
        custom_logger.error(f"Elasticsearch 검색 오류: {e}")
        return f"검색 중 오류가 발생했습니다: {str(e)}"
