"""HTTP 요청/응답 로깅 미들웨어"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logger import custom_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        custom_logger.info(f"요청 시작: {request.method} {request.url.path}")
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        custom_logger.info(
            f"요청 종료: {request.method} {request.url.path} "
            f"(실행 시간: {process_time:.3f}초) "
            f"상태코드: {response.status_code}"
        )

        return response
