import json
import logging

from app.shared.logging_context import (
    RequestContextFilter,
    bind_request_id,
    generate_request_id,
    reset_request_id,
)
from app.shared.utils.logging import JsonFormatter


def test_request_context_filter_adds_request_id(monkeypatch):
    monkeypatch.setenv("LOG_SERVICE", "backend-test")
    rid = generate_request_id()
    token = bind_request_id(rid)
    try:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="hello",
            args=(),
            exc_info=None,
        )
        assert RequestContextFilter().filter(record) is True
        assert record.request_id == rid
        assert record.service == "backend-test"

        payload = json.loads(JsonFormatter().format(record))
        assert payload["request_id"] == rid
        assert payload["service"] == "backend-test"
    finally:
        reset_request_id(token)
