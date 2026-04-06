import { atom } from 'jotai';

// 사이드바 thread 목록 갱신 트리거 — 값을 증가시키면 useHistory가 재조회한다.
export const threadsRefreshAtom = atom<number>(0);
