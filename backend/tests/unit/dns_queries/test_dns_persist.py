from datetime import datetime, timezone

import pytest

from app.features.dns_queries.dns_persist import filter_queries_to_persist, should_persist_query
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate
from app.shared.config import settings


def _query(*, domain: str = "example.com", blocked: bool = False) -> DnsQueryCreate:
    return DnsQueryCreate(
        timestamp=datetime.now(timezone.utc),
        client_ip="10.0.0.2",
        domain=domain,
        query_type="A",
        action="blocked" if blocked else "forwarded",
        blocked=blocked,
    )


@pytest.fixture
def persist_all_dns(monkeypatch):
    monkeypatch.setattr(settings, "PERSIST_ALL_DNS", True)


@pytest.fixture
def blocked_only_persist(monkeypatch):
    monkeypatch.setattr(settings, "PERSIST_ALL_DNS", False)


def test_should_persist_blocked_when_selective(blocked_only_persist):
    assert should_persist_query(_query(blocked=True)) is True
    assert should_persist_query(_query(blocked=False)) is False


def test_should_persist_all_when_flag_enabled(persist_all_dns):
    assert should_persist_query(_query(blocked=False)) is True
    assert should_persist_query(_query(blocked=True)) is True


def test_filter_queries_to_persist(blocked_only_persist):
    queries = [
        _query(domain="allowed.com", blocked=False),
        _query(domain="blocked.com", blocked=True),
        _query(domain="also-allowed.com", blocked=False),
    ]
    persisted = filter_queries_to_persist(queries)
    assert len(persisted) == 1
    assert persisted[0].domain == "blocked.com"
