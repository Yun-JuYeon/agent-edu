"""에이전트 실행 및 SSE 스트리밍 서비스"""

import json
import uuid
from datetime import datetime

from app.utils.logger import log_execution, custom_logger
from app.agents.factory import create_medical_agent


class AgentService:
    def __init__(self):
        self.agent = None

    def _ensure_agent(self):
        if self.agent is None:
            self.agent = create_medical_agent()

    @log_execution
    async def process_query(self, user_messages: str, thread_id: uuid.UUID):
        """사용자 메시지를 에이전트로 처리하고 SSE 청크를 yield합니다."""
        try:
            self._ensure_agent()

            async for chunk in self.agent.astream(
                {"messages": [{"role": "user", "content": user_messages}]},
                config={"configurable": {"thread_id": str(thread_id)}},
                stream_mode="updates",
            ):
                for step, event in chunk.items():
                    if not event:
                        continue

                    # structured_response → 최종 응답
                    if "structured_response" in event:
                        sr = event["structured_response"]
                        yield self._done_response(
                            content=getattr(sr, "content", ""),
                            message_id=getattr(sr, "message_id", None),
                            metadata=getattr(sr, "metadata", None),
                        )
                        continue

                    messages = event.get("messages", [])
                    if not messages:
                        continue
                    msg = messages[0]

                    # 모델 step
                    if step in ("agent", "model", "medical_agent"):
                        tool_calls = getattr(msg, "tool_calls", None)
                        if tool_calls:
                            yield json.dumps({
                                "step": "model",
                                "tool_calls": [t["name"] for t in tool_calls],
                            })
                        else:
                            content = getattr(msg, "content", "")
                            if content:
                                yield self._done_response(content=content)

                    # 도구 step
                    elif step == "tools":
                        yield json.dumps({
                            "step": "tools",
                            "name": getattr(msg, "name", ""),
                            "content": getattr(msg, "content", ""),
                        })

        except Exception as e:
            custom_logger.error(f"process_query 오류: {e}")
            yield self._done_response(
                content="처리 중 오류가 발생했습니다. 다시 시도해주세요.",
                error=str(e),
            )

    def _done_response(
        self,
        content: str,
        message_id: str = None,
        metadata: dict = None,
        error: str = None,
    ) -> str:
        resp = {
            "step": "done",
            "message_id": message_id or str(uuid.uuid4()),
            "role": "assistant",
            "content": content,
            "metadata": dict(metadata) if metadata else {},
            "created_at": datetime.utcnow().isoformat(),
        }
        if error:
            resp["error"] = error
        return json.dumps(resp, ensure_ascii=False)
