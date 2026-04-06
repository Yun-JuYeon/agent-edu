# Agent UI

React + Vite 기반 Agent 채팅 프론트엔드입니다.

## 기술 스택

- **React 19** + **TypeScript**
- **Vite** — 개발 서버 / 번들러
- **Material-UI** — UI 컴포넌트
- **Jotai** — 글로벌 상태 관리
- **@microsoft/fetch-event-source** — SSE 스트리밍
- **Highcharts** — 차트 시각화
- **pnpm** — 패키지 매니저

## 환경 준비

### 1. pnpm 설치

```bash
npm install -g pnpm
```

### 2. 의존성 설치

```bash
cd ui
pnpm install
```

### 3. 환경 변수

`.env` 파일을 생성하고 백엔드 주소를 설정합니다:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 4. 개발 서버 실행

```bash
pnpm dev
```

또는 VSCode `F5` → **`Frontend: Vite Dev`** 선택.

→ `http://localhost:5173` 에서 확인.

### 빌드

```bash
pnpm build
```

## 프로젝트 구조

```
ui/
├── src/
│   ├── components/           # 재사용 컴포넌트
│   │   ├── ChartViewer/      # 차트 표시
│   │   ├── CodeEditor/       # 코드 표시
│   │   ├── GridViewer/       # 데이터 그리드
│   │   ├── Layout/           # 메인 레이아웃 + 사이드바
│   │   ├── MessageInput/     # 메시지 입력창
│   │   └── MyPromptModal/    # 프롬프트 저장 모달
│   ├── hooks/
│   │   ├── useChat.ts        # 채팅 + SSE 스트리밍 훅
│   │   └── useHistory.ts     # 사이드바 스레드 목록 훅
│   ├── pages/
│   │   ├── ChatPage.tsx      # 채팅 화면
│   │   └── InitPage.tsx      # 초기 화면
│   ├── services/
│   │   ├── chatService.ts    # 백엔드 API 호출
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

`fetchEventSource`로 백엔드 `/api/v1/chat` 엔드포인트의 SSE를 구독합니다:

```ts
api.stream(url, body, (step, content, metadata, toolCalls, name) => {
  // step: "model" | "tools" | "done"
  // content: 응답 텍스트
  // metadata: GridData, ChartDefinition 등
});
```

### 사이드바 자동 갱신

채팅 시 새 스레드가 자동으로 사이드바에 추가됩니다:

1. `useChat.handleChunk`에서 `step === 'done'` 시 `threadsRefreshAtom`을 +1
2. `useHistory`의 `useEffect`가 atom 변경 감지 → `getThreads()` 재호출
3. 사이드바 "최근 대화"에 새 스레드 표시

### 디버깅

VSCode에서:
1. `F5` → **`Frontend: Vite Dev`** 선택
2. 또는 **`Full Stack (Backend + Frontend)`**로 백엔드와 동시 실행
3. Chrome DevTools에서 React/TypeScript 디버깅
