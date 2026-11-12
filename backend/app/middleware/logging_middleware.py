"""
TRUSTLENS AI - Request Logging & Process Timing Middleware
Generates unique correlation IDs and measures latency for all API calls.
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from backend.app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        start_time = time.perf_counter()
        
        try:
            response: Response = await call_next(request)
        except Exception as e:
            process_time = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"[{correlation_id}] {request.method} {request.url.path} FAILED in {process_time}ms: {e}")
            raise e

        process_time = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = f"{process_time}ms"

        # Log requests exceeding 150ms or errors
        if response.status_code >= 400 or process_time > 150:
            logger.info(f"[{correlation_id}] {request.method} {request.url.path} -> {response.status_code} ({process_time}ms)")

        return response
