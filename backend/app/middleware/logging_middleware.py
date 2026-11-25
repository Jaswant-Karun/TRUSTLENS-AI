"""
TRUSTLENS AI - Request Logging & Process Timing Middleware
Generates unique request/correlation IDs, emits structured latency logs,
and attaches X-Request-ID, X-Correlation-ID, and X-Process-Time headers.
"""

import json
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from backend.app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = (
            request.headers.get("X-Request-ID")
            or request.headers.get("X-Correlation-ID")
            or str(uuid.uuid4())
        )
        request.state.request_id = request_id
        request.state.correlation_id = request_id

        start_time = time.perf_counter()

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            process_time = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                json.dumps({
                    "event": "http_request_error",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "latency_ms": process_time,
                    "error": exc.__class__.__name__,
                })
            )
            raise

        process_time = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time}ms"

        if response.status_code >= 400 or process_time > 150:
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} -> {response.status_code} ({process_time}ms)"
            )

        return response
