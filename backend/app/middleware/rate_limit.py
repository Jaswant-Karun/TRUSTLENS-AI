"""
TRUSTLENS AI - Rate Limiting Middleware
Applies IP-based sliding window rate limiting to protect API endpoints from abuse.
"""

import re
import time
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from backend.app.config.settings import settings
from backend.app.services.abuse_service import abuse_service

SUSPICIOUS_QUERY_RE = re.compile(r"(\$where|\$ne|\$gt|\$regex|\.\./|%2e%2e|<script)", re.IGNORECASE)
MAX_REQUEST_BODY_BYTES = 12 * 1024 * 1024  # 12 MB resource-exhaustion guard


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_records: Dict[str, List[float]] = {}
        self.auth_request_records: Dict[str, List[float]] = {}

    def _clean_old_records(self, timestamps: List[float], window_seconds: float) -> List[float]:
        cutoff = time.time() - window_seconds
        return [ts for ts in timestamps if ts > cutoff]

    async def dispatch(self, request: Request, call_next) -> Response:
        import os
        client_ip = request.client.host if request.client else "unknown"

        # Resource exhaustion guard on declared Content-Length
        content_len = request.headers.get("content-length")
        if content_len and content_len.isdigit() and int(content_len) > MAX_REQUEST_BODY_BYTES:
            await abuse_service.record_suspicious_event(
                "oversized_payload_blocked", client_ip, request.url.path, f"Content-Length={content_len}", raise_alert=True
            )
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"error": "PayloadTooLarge", "message": "Request payload exceeds maximum allowed size."},
            )

        # Suspicious query/path probe detection (URL-decoded to prevent %3C / %24 / %2e bypass)
        from urllib.parse import unquote
        raw_qs = unquote(str(request.url.query or ""))
        raw_path = unquote(str(request.url.path or ""))
        if SUSPICIOUS_QUERY_RE.search(raw_qs) or ".." in raw_path:
            await abuse_service.record_suspicious_event(
                "suspicious_request_probe", client_ip, request.url.path, "Blocked suspicious query/path pattern", raise_alert=True, severity="high"
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "BadRequest", "message": "Invalid or disallowed request parameters."},
            )

        # Exempt during automated test runs unless explicitly testing rate limits
        if (os.environ.get("TESTING") == "true" or getattr(request.app.state, "testing", False)) and not getattr(request.app.state, "force_rate_limit_test", False):
            return await call_next(request)

        # Exempt Swagger docs & health checks from rate limiting
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/", f"{settings.API_V1_STR}/health"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0  # 1 minute

        # Dedicated stricter limit for authentication routes
        is_auth_route = "/auth/" in request.url.path

        if is_auth_route:
            records = self.auth_request_records.get(client_ip, [])
            records = self._clean_old_records(records, window)
            if len(records) >= settings.AUTH_RATE_LIMIT_PER_MINUTE:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "RateLimitExceeded",
                        "message": f"Too many authentication attempts. Limit is {settings.AUTH_RATE_LIMIT_PER_MINUTE} per minute.",
                    },
                    headers={"Retry-After": "60"},
                )
            records.append(now)
            self.auth_request_records[client_ip] = records
        else:
            records = self.request_records.get(client_ip, [])
            records = self._clean_old_records(records, window)
            if len(records) >= settings.RATE_LIMIT_PER_MINUTE:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "RateLimitExceeded",
                        "message": f"Too many requests. Limit is {settings.RATE_LIMIT_PER_MINUTE} per minute.",
                    },
                    headers={"Retry-After": "60"},
                )
            records.append(now)
            self.request_records[client_ip] = records

        return await call_next(request)

