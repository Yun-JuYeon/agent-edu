"""Elasticsearch 클라이언트 관리 및 검색 서비스"""

from elasticsearch import Elasticsearch

from app.core.config import settings
from app.utils.logger import custom_logger


class ElasticsearchService:
    """Elasticsearch 연결 및 검색을 담당하는 서비스"""

    def __init__(self):
        self._client: Elasticsearch | None = None

    @property
    def client(self) -> Elasticsearch:
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self) -> Elasticsearch:
        """Elasticsearch 클라이언트 생성"""
        kwargs = {
            "hosts": [settings.ELASTICSEARCH_URL],
            "verify_certs": False,
        }
        if settings.ELASTICSEARCH_USERNAME and settings.ELASTICSEARCH_PASSWORD:
            kwargs["basic_auth"] = (
                settings.ELASTICSEARCH_USERNAME,
                settings.ELASTICSEARCH_PASSWORD,
            )
        return Elasticsearch(**kwargs)

    # 검색 결과에서 제외할 메타 필드
    _SKIP_FIELDS = {"c_id", "domain", "source", "source_spec", "creation_year"}

    def search(self, query: str, size: int = 3) -> str:
        """의료 데이터를 검색하여 간결한 문자열로 반환합니다."""
        index = settings.ELASTICSEARCH_INDEX

        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content", "title", "keyword", "*"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            },
            "size": size,
        }

        response = self.client.search(index=index, body=search_body)
        hits = response.get("hits", {}).get("hits", [])

        if not hits:
            return f"'{query}'에 대한 검색 결과가 없습니다."

        results = []
        for i, hit in enumerate(hits, 1):
            source = hit.get("_source", {})
            # content 필드 우선, 없으면 주요 필드만 간결하게
            content = source.get("content", "")
            if content:
                # 너무 긴 content는 앞부분만
                summary = content[:500] + ("..." if len(content) > 500 else "")
            else:
                summary = " / ".join(
                    f"{k}: {v}" for k, v in source.items()
                    if v and k not in self._SKIP_FIELDS
                )
            results.append(f"[{i}] {summary}")

        return "\n\n".join(results)

    def health_check(self) -> bool:
        """Elasticsearch 연결 상태를 확인합니다."""
        try:
            return self.client.ping()
        except Exception as e:
            custom_logger.error(f"Elasticsearch 연결 실패: {e}")
            return False
