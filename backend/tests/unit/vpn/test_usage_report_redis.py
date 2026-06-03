from datetime import datetime, timezone
from unittest.mock import patch

from app.features.vpn.schemas.usage import UsageReportRequest
from app.features.vpn.services.usage_redis_store import UsageRecordResult
from app.features.vpn.services.usage_service import UsageService
from app.features.vpn.schemas.usage_history import UsageHistoryPoint
from app.features.vpn.schemas.usage_live import DeviceUsageLiveItem


def _payload() -> UsageReportRequest:
    return UsageReportRequest(
        device_id="dev-x",
        interval_sec=5.0,
        rx_bytes=0,
        tx_bytes=0,
        delta_rx_bytes=1024,
        delta_tx_bytes=0,
    )


def test_report_usage_broadcasts_when_redis_records(db_session):
    now_point = UsageHistoryPoint(
        recorded_at=datetime.now(timezone.utc),
        rx_mib_per_sec=0.1,
        tx_mib_per_sec=0.0,
        total_mib_per_sec=0.1,
        reporting_clients=1,
    )
    live_item = DeviceUsageLiveItem(
        device_id=None,
        vpn_device_id="dev-x",
        client_ip=None,
        recorded_at=now_point.recorded_at,
        interval_sec=5.0,
        rx_bytes=0,
        tx_bytes=0,
        delta_rx_bytes=1024,
        delta_tx_bytes=0,
        rx_mib_per_sec=0.1,
        tx_mib_per_sec=0.0,
        total_mib_per_sec=0.1,
    )
    record_result = UsageRecordResult(aggregate_point=now_point, live_items=[live_item])

    with patch("app.features.vpn.services.usage_service.redis_available", return_value=True):
        with patch(
            "app.features.vpn.services.usage_service.usage_redis_store.record_sample",
            return_value=record_result,
        ):
            with patch(
                "app.features.vpn.services.usage_service.usage_redis_store.enrich_live_items",
                return_value=[live_item],
            ):
                with patch(
                    "app.features.vpn.services.usage_service.broadcast_usage_update",
                ) as mock_broadcast:
                    with patch("app.features.vpn.services.usage_service.settings") as mock_settings:
                        mock_settings.USAGE_PERSIST_SAMPLES = False
                        mock_settings.BANDWIDTH_ALERT_MIB_PER_SEC = 999.0
                        mock_settings.USAGE_LIVE_MAX_AGE_SEC = 45
                        resp = UsageService(db_session).report_usage(_payload())

    assert resp.stored is True
    mock_broadcast.assert_called_once()
