from datetime import datetime, timezone
from unittest.mock import patch

import fakeredis
import pytest

from app.features.vpn.schemas.usage import UsageReportRequest
from app.features.vpn.services import usage_redis_store


@pytest.fixture
def fake_redis():
    client = fakeredis.FakeRedis(decode_responses=True)
    with patch("app.features.vpn.services.usage_redis_store.get_redis", return_value=client):
        with patch("app.features.vpn.services.usage_redis_store.redis_available", return_value=True):
            yield client


def _sample(device_id: str = "dev-1", *, rx_delta: int = 5 * 1024 * 1024) -> UsageReportRequest:
    return UsageReportRequest(
        device_id=device_id,
        interval_sec=5.0,
        rx_bytes=10 * 1024 * 1024,
        tx_bytes=1 * 1024 * 1024,
        delta_rx_bytes=rx_delta,
        delta_tx_bytes=1 * 1024 * 1024,
    )


def test_record_sample_trims_and_aggregates(fake_redis):
    with patch("app.features.vpn.services.usage_redis_store._ms_now") as mock_now:
        base_ms = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
        mock_now.side_effect = [base_ms, base_ms + 1000]

        usage_redis_store.record_sample(_sample("dev-a"))
        result = usage_redis_store.record_sample(_sample("dev-b", rx_delta=2 * 1024 * 1024))

    assert result.aggregate_point.reporting_clients == 2
    assert result.aggregate_point.total_mib_per_sec == pytest.approx(1.8, rel=0.01)
    assert len(result.live_items) == 2

    agg_count = fake_redis.zcard(usage_redis_store.SERVER_AGGREGATE_KEY)
    assert agg_count == 2


def test_list_history_returns_points_in_window(fake_redis):
    usage_redis_store.record_sample(_sample("dev-a"))
    history = usage_redis_store.list_history(minutes=60)
    assert len(history.points) == 1
    assert history.points[0].reporting_clients == 1


def test_list_live_empty_without_devices(fake_redis, db_session):
    live = usage_redis_store.list_live(db_session, max_age_sec=60)
    assert live.items == []
