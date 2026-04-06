# Medical Agent — UI

React + Vite + TypeScript 기반 채팅 프론트엔드.

## 스택

- **React 19** + **TypeScript**
- **Vite**
- **Material-UI**
- **Jotai** — 글로벌 상태
- **@microsoft/fetch-event-source** — SSE 스트리밍
- **Highcharts** — 차트
- **pnpm**

## 셋업

```bash
# 1. pnpm 설치 (최초 1회)
npm install -g pnpm

# 2. 의존성
cd ui
pnpm install

# 3. 환경 변수
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# 4. 실행
pnpm dev   # http://localhost:5173
```

또는 VSCode `F5` → **Frontend: Vite Dev**.

빌드: `pnpm build`

## 디렉토리

```
ui/
├── src/
│   ├── components/
│   │   ├── ChartViewer/
│   │   ├── CodeEditor/
│   │   ├── GridViewer/
│   │   ├── Layout/           # 메인 레이아웃 + 사이드바
│   │   ├── MessageInput/
│   │   └── MyPromptModal/
│   ├── hooks/
│   │   ├── useChat.ts        # 채팅 + SSE
│   │   └── useHistory.ts     # 사이드바 스레드 목록
│   ├── pages/
│   │   ├── ChatPage.tsx
│   │   └── InitPage.tsx
│   ├── services/
│   │   ├── chatService.ts    # API 호출
│   │   └── common.ts         # axios + SSE wrapper
│   ├── store/                # Jotai atoms
│   │   ├── answer.ts
│   │   ├── message.ts
│   │   ├── question.ts
│   │   ├── prompts.ts
│   │   └── threads.ts        # 사이드바 갱신 트리거
│   ├── types/
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
├── vite.config.ts
└── package.json
```

## 핵심 흐름

### SSE 스트리밍 ([services/common.ts](src/services/common.ts))

`fetchEventSource`로 백엔드 `/api/v1/chat` SSE를 구독하고 청크별로 콜백 호출:

```ts
api.stream(url, body, (step, content, metadata, toolCalls, name) => {
  // step: "model" | "tools" | "done"
});
```

### 사이드바 자동 갱신

새 채팅 시작 시 사이드바가 자동으로 갱신됩니다:

1. `useChat.handleChunk`에서 `step === 'done'` 시 `threadsRefreshAtom`을 +1
2. `useHistory`의 `useEffect`가 atom 변경을 감지 → `getThreads()` 재호출
3. "최근 대화" 목록에 새 스레드 표시
