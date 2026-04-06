# Agent Education Template

LangChain v1.0 기반 의료 Q&A 에이전트 교육용 풀스택 템플릿입니다. FastAPI 백엔드와 React 프론트엔드, Elasticsearch RAG 검색을 포함합니다.

## 주요 기능

- **LangChain `create_agent`** 기반 에이전트 (이전 `create_react_agent` 대체)
- **Intent 분류 미들웨어** — `gpt-4o-mini` + structured output으로 일반 대화/의료 질문 분류
- **Elasticsearch RAG** — 의료 데이터 검색 도구
- **SSE 스트리밍** — 실시간 토큰/도구 호출 스트리밍
- **인메모리 스레드 저장소** — 사이드바에 자동 등록되는 대화 관리
- **VSCode 디버거 통합** — F5로 백엔드/프론트엔드 동시 디버깅

## 프로젝트 구조

```
agent-edu/
├── agent/                    # FastAPI 백엔드 (Python 3.11+)
│   └── app/
│       ├── agents/           # LangChain 에이전트
│       │   ├── factory.py    # create_agent 팩토리
│       │   ├── prompts/      # 시스템 프롬프트
│       │   ├── intent/       # Intent 분류 (schema/classifier/middleware)
│       │   └── medical/      # 의료 도메인 도구
│       ├── api/              # FastAPI 라우트 + 미들웨어
│       ├── core/             # 환경 설정
│       ├── models/           # Pydantic 모델
│       ├── services/         # 비즈니스 로직 (agent, ES, thread store)
│       └── utils/            # 로거 등 유틸
├── ui/                       # React + Vite 프론트엔드
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       ├── services/
│       └── store/            # Jotai atoms
└── .vscode/
    └── launch.json           # 디버거 설정
```

## 빠른 시작

### 1. 백엔드

```bash
cd agent
cp env.sample .env
# .env 파일을 열어 OPENAI_API_KEY와 ELASTICSEARCH 설정값 입력

uv sync                                                  # 의존성 설치
uv run uvicorn app.main:app --reload --port 8000
```

→ `http://localhost:8000/docs` 에서 API 문서 확인

자세한 내용은 [agent/README.md](agent/README.md) 참고.

### 2. 프론트엔드

```bash
cd ui
pnpm install
pnpm dev
```

→ `http://localhost:5173` 에서 채팅 UI 확인

자세한 내용은 [ui/README.md](ui/README.md) 참고.

### 3. VSCode 디버거 (권장)

VSCode에서 `F5` → **`Full Stack (Backend + Frontend)`** 선택 시 백엔드/프론트엔드가 동시에 기동됩니다.

| 구성 | 설명 |
|---|---|
| `Backend: FastAPI` | uvicorn + debugpy로 백엔드 디버깅 |
| `Frontend: Vite Dev` | pnpm dev로 프론트엔드 기동 |
| `Full Stack` | 위 두 개 동시 실행 |

## 동작 흐름

```
사용자 입력
   ↓
[Frontend] useChat → SSE POST /api/v1/chat
   ↓
[Backend] thread_store.add_user_message
   ↓
agent.astream() → intent_middleware
   ↓
   ├─ GENERAL → tools=[] → LLM 직접 응답
   └─ MEDICAL → search_medical_data (Elasticsearch)
                ↓
                LLM이 검색 결과로 답변 생성
   ↓
SSE 스트림으로 청크 전송 → Frontend 렌더
   ↓
done 청크 → thread_store.add_assistant_message
   ↓
useHistory가 사이드바 갱신
```

## 환경 변수

[agent/env.sample](agent/env.sample) 참고. 주요 값:

- `OPENAI_API_KEY` — OpenAI API 키
- `OPENAI_MODEL` — 메인 에이전트 모델 (예: `gpt-5-mini`)
- `INTENT_CLASSIFIER_MODEL` — Intent 분류 전용 경량 모델 (기본: `gpt-4o-mini`)
- `ELASTICSEARCH_URL` / `ELASTICSEARCH_INDEX` / `ELASTICSEARCH_USERNAME` / `ELASTICSEARCH_PASSWORD`

> ⚠️ `.env` 파일은 절대 커밋하지 마세요. `.gitignore`에 등록되어 있습니다.
