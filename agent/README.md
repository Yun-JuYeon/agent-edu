# Medical Agent — Backend

FastAPI + LangChain v1.0 기반 의료 Q&A 에이전트 백엔드.

## 스택

- **FastAPI** + SSE 스트리밍
- **LangChain v1.0** `create_agent` (구 `create_react_agent` 대체)
- **LangGraph** `InMemorySaver` checkpointer
- **OpenAI** — `gpt-5-mini` (메인) + `gpt-4o-mini` (intent 분류)
- **Elasticsearch** — RAG 의료 데이터 검색
- **uv** — 패키지 매니저

## 셋업

```bash
# 1. uv 설치 (최초 1회)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 의존성
cd agent
uv sync

# 3. 환경 변수
cp env.sample .env
# .env 열어서 OPENAI_API_KEY, ELASTICSEARCH_* 채우기

# 4. 실행
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

→ Swagger UI: `http://localhost:8000/docs`

또는 VSCode `F5` → **Backend: FastAPI**.

## 디렉토리

```
agent/
├── app/
│   ├── agents/
│   │   ├── factory.py                # create_medical_agent()
│   │   ├── prompts/
│   │   │   ├── medical.py            # 의료 Q&A 프롬프트
│   │   │   └── intent.py             # Intent 분류 프롬프트
│   │   ├── intent/
│   │   │   ├── schemas.py            # IntentClassification (Pydantic)
│   │   │   ├── classifier.py         # with_structured_output 분류기
│   │   │   └── middleware.py         # @wrap_model_call 미들웨어
│   │   └── medical/
│   │       └── tools.py              # search_medical_data
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py               # POST /api/v1/chat (SSE)
│   │   │   └── threads.py            # GET/DELETE /api/v1/threads
│   │   └── middleware/
│   │       └── logging.py            # HTTP 로깅 미들웨어
│   ├── core/config.py
│   ├── models/chat.py
│   ├── services/
│   │   ├── agent_service.py          # 에이전트 실행 + SSE 스트리밍
│   │   ├── elasticsearch_service.py  # ES 클라이언트 + 검색
│   │   └── thread_store.py           # 인메모리 대화 저장소
│   ├── utils/logger.py
│   └── main.py
├── tests/
├── env.sample
├── pyproject.toml
└── README.md
```

## 핵심 컴포넌트

### Intent 미들웨어 ([agents/intent/](app/agents/intent/))

`@wrap_model_call` 미들웨어가 에이전트 모델 호출 전에 가로채서 사용자 메시지의 intent를 판별합니다.

```python
@wrap_model_call
async def intent_middleware(request, handler):
    user_text = _extract_last_user_text(request.messages)
    result = await classify_intent(user_text)  # gpt-4o-mini, structured output

    if result.intent == "GENERAL":
        return await handler(request.override(tools=[]))  # 도구 제거
    return await handler(request)
```

분류기는 `with_structured_output(IntentClassification)`로 `Literal["MEDICAL", "GENERAL"]` 응답을 강제합니다.

### ThreadStore ([services/thread_store.py](app/services/thread_store.py))

`POST /chat` 진입 시 user 메시지가 자동 저장되고, 첫 메시지면 새 스레드가 생성됩니다. 스트림 종료 시 assistant 응답도 같은 스레드에 추가됩니다.

> 프로세스 메모리 기반이므로 서버 재시작 시 휘발됩니다. 영속화가 필요하면 동일 인터페이스(`add_user_message`, `add_assistant_message`, `list_threads`, `get_thread`, `delete_thread`)로 DB 백엔드를 갈아끼우면 됩니다.

## API

| Method | Path | 설명 |
|---|---|---|
| `GET` | `/health` | 헬스 체크 |
| `POST` | `/api/v1/chat` | 채팅 (SSE 스트리밍) |
| `GET` | `/api/v1/threads` | 스레드 목록 |
| `GET` | `/api/v1/threads/{id}` | 스레드 상세 |
| `DELETE` | `/api/v1/threads/{id}` | 스레드 삭제 |

### Chat 예시

```bash
curl -N -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"thread_id":"11111111-1111-1111-1111-111111111111","message":"당뇨병 증상이 뭐야?"}'
```

응답:
```
data: {"step": "model", "tool_calls": ["search_medical_data"]}
data: {"step": "tools", "name": "search_medical_data", "content": "..."}
data: {"step": "done", "message_id": "...", "content": "...", "metadata": {}, "created_at": "..."}
```
