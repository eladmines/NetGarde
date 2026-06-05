"""Request-scoped logging context (request_id) for structured CloudWatch queries."""

from __future__ import annotations

import contextvars
import logging
import os
from typing import Optional
from uuid import uuid4

request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)


def generate_request_id() -> str:
    return str(uuid4())


def get_request_id() -> Optional[str]:
    return request_id_var.get()


def bind_request_id(request_id: str) -> contextvars.Token:
    return request_id_var.set(request_id)


def reset_request_id(token: contextvars.Token) -> None:
    request_id_var.reset(token)


_LOG_RECORD_RESERVED = frozenset({
    "args", "asctime", "created", "exc_info", "exc_text", "filename",
    "funcName", "levelname", "levelno", "lineno", "message", "module",
    "msecs", "msg", "name", "pathname", "process", "processName",
    "relativeCreated", "stack_info", "thread", "threadName",
})


def structured_extra(event: str, **fields: object) -> dict[str, object]:
    """Build logger extra={...} with a stable event name for CloudWatch Insights."""
    safe: dict[str, object] = {"event": event}
    for key, value in fields.items():
        out_key = f"ctx_{key}" if key in _LOG_RECORD_RESERVED else key
        safe[out_key] = value
    return safe


class RequestContextFilter(logging.Filter):
    """Attach service and request_id to every log record for JSON output."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.service = os.getenv("LOG_SERVICE", "backend")
        rid = get_request_id()
        if rid:
            record.request_id = rid
        return True
