"""인메모리 스레드(대화) 저장소"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.utils.logger import custom_logger


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ThreadStore:
    """프로세스 메모리에 대화를 보관하는 저장소.

    재시작 시 사라지지만, 데모/교육용으로는 충분합니다.
    필요 시 동일 인터페이스로 DB 백엔드로 교체 가능합니다.
    """

    def __init__(self):
        # thread_id -> {thread_id, title, created_at, updated_at, messages: [...]}
        self._threads: dict[str, dict] = {}

    # ---------- 조회 ----------

    def list_threads(self) -> list[dict]:
        """대화 목록을 최신순으로 반환합니다."""
        items = [
            {
                "thread_id": t["thread_id"],
                "title": t["title"],
                "created_at": t["created_at"],
                "updated_at": t["updated_at"],
                "is_favorited": t.get("is_favorited", False),
            }
            for t in self._threads.values()
        ]
        items.sort(key=lambda x: x["updated_at"], reverse=True)
        return items

    def get_thread(self, thread_id: str) -> Optional[dict]:
        return self._threads.get(thread_id)

    # ---------- 변경 ----------

    def add_user_message(self, thread_id: str, content: str) -> None:
        thread = self._threads.get(thread_id)
        now = _now_iso()
        message = {
            "message_id": str(uuid.uuid4()),
            "role": "user",
            "content": content,
            "is_favorited": False,
            "created_at": now,
        }

        if thread is None:
            # 새 스레드 생성: 첫 메시지로 제목을 자동 생성
            title = content.strip().splitlines()[0][:40] or "새 대화"
            self._threads[thread_id] = {
                "thread_id": thread_id,
                "title": title,
                "created_at": now,
                "updated_at": now,
                "is_favorited": False,
                "messages": [message],
            }
            custom_logger.info(f"[ThreadStore] 새 스레드 생성: {thread_id} ({title})")
        else:
            thread["messages"].append(message)
            thread["updated_at"] = now

    def add_assistant_message(
        self,
        thread_id: str,
        content: str,
        message_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        thread = self._threads.get(thread_id)
        if thread is None:
            custom_logger.warning(
                f"[ThreadStore] assistant 메시지 추가 실패 - 존재하지 않는 thread: {thread_id}"
            )
            return

        thread["messages"].append({
            "message_id": message_id or str(uuid.uuid4()),
            "role": "assistant",
            "content": content,
            "metadata": metadata or {},
            "created_at": _now_iso(),
        })
        thread["updated_at"] = _now_iso()

    def delete_thread(self, thread_id: str) -> bool:
        return self._threads.pop(thread_id, None) is not None


# 싱글톤
thread_store = ThreadStore()
