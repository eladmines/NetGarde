from datetime import datetime, timezone
from unittest.mock import patch

from app.features.dns_queries.schemas.dns_query import DnsQueryCreate
from app.features.dns_queries.services.dns_query_service import DnsQueryService


def _blocked_query(**kwargs):
    defaults = {
        "timestamp": datetime.now(timezone.utc),
        "client_ip": "10.0.0.80",
        "domain": "blocked.test",
        "blocked": True,
    }
    defaults.update(kwargs)
    return DnsQueryCreate(**defaults)


def test_create_query_persists_blocked(db_session, dns_ingest_env):
    svc = DnsQueryService()
    result = svc.create_query(_blocked_query(), db_session)
    assert result.domain == "blocked.test"
    assert result.id > 0


def test_create_query_skips_allowed_when_selective(db_session, dns_live_stats_env):
    svc = DnsQueryService()
    result = svc.create_query(
        _blocked_query(domain="allowed.test", blocked=False),
        db_session,
    )
    assert result.id == 0


@patch("app.features.dns_queries.services.dns_query_service.ingest_stats")
def test_get_grouped_by_site_uses_live_stats(mock_stats, db_session, dns_live_stats_env):
    mock_stats.get_grouped_sites.return_value = {"sites": [], "source": "memory"}
    svc = DnsQueryService()
    result = svc.get_grouped_by_site(db_session, limit=10)
    mock_stats.get_grouped_sites.assert_called_once()
    assert result["source"] == "memory"
