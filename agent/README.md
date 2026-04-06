# Agent Backend

FastAPI + LangChain v1.0 기반 의료 Q&A 에이전트 백엔드입니다.

## 기술 스택

- **FastAPI** — REST API + SSE 스트리밍
- **LangChain v1.0** — `create_agent` (구 `create_react_agent` 대체)
- **LangGraph** — checkpointer (InMemorySaver)
- **OpenAI** — `gpt-5-mini` (메인) + `gpt-4o-mini` (intent 분류)
- **Elasticsearch** — RAG 의료 데이터 검색
- **uv** — Python 패키지 매니저

## 환경 준비

### 1. 사전 요구사항

- Python 3.11 이상 ~ 3.13 이하
- `uv` 패키지 매니저:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. 의존성 설치

```bash
cd agent
uv sync
```

→ `.venv/` 가상환경이 자동 생성됩니다.

### 3. 환경 변수 설정

```bash
cp env.sample .env
```

`.env` 파일을 열고 다음 값을 입력하세요:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5-mini
INTENT_CLASSIFIER_MODEL=gpt-4o-mini

ELASTICSEARCH_URL=https://your-es-host
ELASTICSEARCH_INDEX=your-index
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=...
```

### 4. 서버 실행

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

또는 VSCode `F5` → **`Backend: FastAPI`** 선택.

→ `http://localhost:8000/docs` 에서 Swagger UI 확인.

## 프로젝트 구조

```
agent/
├── app/
│   ├── agents/                       # LangChain 에이전트
│   │   ├── factory.py                # create_medical_agent()
│   │   ├── prompts/                  # 시스템 프롬프트
│   │   │   ├── medical.py            # 의료 Q&A 프롬프트
│   │   │   └── intent.py             # Intent 분류 프롬프트
│   │   ├── intent/                   # Intent 분류 기능
│   │   │   ├── schemas.py            # IntentClassification (Pydantic)
│   │   │   ├── classifier.py         # with_structured_output 분류기
│   │   │   └── middleware.py         # @wrap_model_call 미들웨어
│   │   └── medical/                  # 의료 도메인
│   │       └── tools.py              # search_medical_data
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py               # POST /api/v1/chat (SSE)
│   │   │   └── threads.py            # GET/DELETE /api/v1/threads
│   │   └── middleware/
│   │       └── logging.py            # HTTP 로깅 미들웨어
│   ├── core/
│   │   └── config.py                 # Pydantic Settings
│   ├── models/                       # Pydantic 요청/응답 모델
│   │   └── chat.py
│   ├── services/
│   │   ├── agent_service.py          # 에이전트 실행/SSE 스트리밍
│   │   ├── elasticsearch_service.py  # ES 클라이언트 + 검색
│   │   └── thread_store.py           # 인메모리 대화 저장소
│   ├── utils/
│   │   └── logger.py                 # custom_logger + @log_execution
│   └── main.py                       # FastAPI 앱 진입점
├── tests/
├── env.sample                        # 환경변수 템플릿
├── pyproject.toml
└── README.md
```

## 핵심 컴포넌트

### Intent 분류 미들웨어 ([agents/intent/](app/agents/intent/))

`@wrap_model_call` 미들웨어가 에이전트 모델 호출 전에 가로챕니다:

```python
@wrap_model_call
async def intent_middleware(request, handler):
    intent = await classify_intent(user_text)  # gpt-4o-mini, structured output
    if intent == "GENERAL":
        return await handler(request.override(tools=[]))  # RAG 건너뜀
    return await handler(request)
```

- **GENERAL** (인사/잡담) → 도구 제거 후 LLM만 호출
- **MEDICAL** (의료 질문) → `search_medical_data` 도구 사용 가능

### 인메모리 스레드 저장소 ([services/thread_store.py](app/services/thread_store.py))

`POST /chat` 진입 시 user 메시지가 자동 저장되고, 첫 메시지면 새 스레드가 생성됩니다. 스트림 종료 시 assistant 응답도 저장됩니다.

> ⚠️ 프로세스 메모리 기반이라 서버 재시작 시 사라집니다. DB 영속화가 필요하면 동일 인터페이스로 백엔드 교체 가능합니다.

## API 엔드포인트

| Method | Path | 설명 |
|---|---|---|
| `GET` | `/health` | 헬스 체크 |
| `POST` | `/api/v1/chat` | 채팅 (SSE 스트리밍) |
| `GET` | `/api/v1/threads` | 스레드 목록 |
| `GET` | `/api/v1/threads/{id}` | 스레드 상세 |
| `DELETE` | `/api/v1/threads/{id}` | 스레드 삭제 |

### Chat 요청 예시

```bash
curl -N -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"thread_id":"11111111-1111-1111-1111-111111111111","message":"당뇨병 증상이 뭐야?"}'
```

응답은 SSE 청크로 옵니다:
```
data: {"step": "model", "tool_calls": ["search_medical_data"]}
data: {"step": "tools", "name": "search_medical_data", "content": "..."}
data: {"step": "done", "message_id": "...", "role": "assistant", "content": "...", "metadata": {}, "created_at": "..."}
```
