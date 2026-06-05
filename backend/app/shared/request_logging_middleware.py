"""HTTP request correlation and concise access logging."""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.shared.logging_context import (
    bind_request_id,
    generate_request_id,
    reset_request_id,
)

logger = logging.getLogger("app.http")

_ACCESS_LOG_SKIP_PATHS = frozenset({"/health"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        incoming = request.headers.get("X-Request-ID", "").strip()
        request_id = incoming or generate_request_id()
        token = bind_request_id(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            if request.url.path not in _ACCESS_LOG_SKIP_PATHS:
                duration_ms = round((time.perf_counter() - started) * 1000, 2)
                logger.info(
                    "request completed",
                    extra={
                        "event": "http_request",
                        "http_method": request.method,
                        "http_path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                    },
                )
            return response
        except Exception:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.exception(
                "request failed",
                extra={
                    "event": "http_request_failed",
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            raise
        finally:
            reset_request_id(token)
