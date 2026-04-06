# Medical Agent

LangChain v1.0 기반 의료 Q&A 에이전트. 인사 같은 일반 대화는 LLM이 바로 답하고, 의료 질문은 Elasticsearch RAG로 검색해 근거 있는 답변을 내놓습니다.

FastAPI 백엔드와 React 프론트엔드, SSE 스트리밍, 인메모리 대화 관리를 포함한 풀스택 구성입니다.

## 핵심 설계

- **`create_agent`** — LangChain v1.0의 신규 에이전트 팩토리 사용
- **Intent 미들웨어** — `gpt-4o-mini`로 사용자 메시지를 `MEDICAL` / `GENERAL` 분류 후 도구 사용 여부 결정
- **Structured Output** — `with_structured_output(IntentClassification)`로 분류 결과 강제
- **Elasticsearch RAG** — `search_medical_data` 도구가 의료 문서 검색
- **SSE 스트리밍** — 모델/도구/완료 단계를 실시간으로 프론트에 전달
- **인메모리 ThreadStore** — 채팅 시작 시 자동으로 스레드 생성, 사이드바에 즉시 반영

## 디렉토리

```
.
├── agent/                    # FastAPI 백엔드
│   └── app/
│       ├── agents/
│       │   ├── factory.py    # create_agent 조립
│       │   ├── prompts/      # 시스템 프롬프트
│       │   ├── intent/       # schemas / classifier / middleware
│       │   └── medical/      # 의료 도메인 도구
│       ├── api/              # routes + middleware
│       ├── core/             # config
│       ├── services/         # agent / elasticsearch / thread_store
│       └── main.py
├── ui/                       # React + Vite 프론트엔드
│   └── src/
│       ├── components/
│       ├── hooks/            # useChat, useHistory
│       ├── pages/
│       ├── services/         # SSE wrapper
│       └── store/            # Jotai atoms
└── .vscode/launch.json       # 디버거 설정
```

## 실행

### 백엔드
```bash
cd agent
cp env.sample .env   # OPENAI_API_KEY, ELASTICSEARCH_* 채우기
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### 프론트엔드
```bash
cd ui
pnpm install
pnpm dev   # http://localhost:5173
```

### VSCode
`F5` → **Full Stack (Backend + Frontend)** 선택 시 둘 다 디버거 모드로 동시 기동.

## 동작

```
사용자 입력
   │
   ▼
useChat → POST /api/v1/chat (SSE)
   │
   ▼
thread_store.add_user_message  ← 첫 메시지면 새 스레드 생성
   │
   ▼
agent.astream() → intent_middleware
   │
   ├─ GENERAL → tools=[] → LLM 직접 응답
   └─ MEDICAL → search_medical_data (ES) → LLM이 답변
   │
   ▼
done 청크 → thread_store.add_assistant_message
   │
   ▼
useHistory가 사이드바 갱신 (threadsRefreshAtom)
```

자세한 내용은 [agent/README.md](agent/README.md), [ui/README.md](ui/README.md) 참고.
