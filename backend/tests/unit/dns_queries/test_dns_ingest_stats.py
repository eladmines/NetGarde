from datetime import datetime, timezone

from app.features.dns_queries.dns_ingest_stats import DnsIngestStats
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate


def _q(domain: str, *, blocked: bool = False, client_ip: str = "10.0.0.2") -> DnsQueryCreate:
    return DnsQueryCreate(
        timestamp=datetime.now(timezone.utc),
        client_ip=client_ip,
        domain=domain,
        query_type="A",
        action="blocked" if blocked else "forwarded",
        blocked=blocked,
    )


def test_ingest_stats_counts():
    stats = DnsIngestStats()
    stats.record([
        _q("google.com"),
        _q("google.com"),
        _q("blocked.com", blocked=True),
    ])
    result = stats.get_stats()
    assert result["total_queries"] == 3
    assert result["blocked_queries"] == 1
    assert result["allowed_queries"] == 2
    assert result["source"] == "live"


def test_ingest_stats_grouped_sites():
    stats = DnsIngestStats()
    stats.record([_q("www.ynet.co.il"), _q("ynet.co.il")])
    sites = stats.get_grouped_sites(limit=10)
    assert sites["total_sites"] == 1
    assert sites["sites"][0]["root_domain"] == "ynet.co.il"
    assert sites["sites"][0]["total_queries"] == 2
