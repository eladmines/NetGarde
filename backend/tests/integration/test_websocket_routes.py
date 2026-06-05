from unittest.mock import patch

from app.features.vpn.schemas.usage_history import UsageHistoryResponse
from app.features.vpn.schemas.usage_live import DeviceUsageLiveResponse


@patch("app.features.devices.routes.device_route.UsageService")
def test_device_usage_websocket_ping(mock_usage_cls, api_client):
    mock_usage_cls.return_value.list_usage_history.return_value = UsageHistoryResponse(
        points=[], minutes=60
    )
    mock_usage_cls.return_value.list_live_bandwidth.return_value = DeviceUsageLiveResponse(
        items=[], max_age_sec=60
    )

    with api_client.websocket_connect("/devices/usage/ws") as ws:
        snapshot = ws.receive_text()
        assert "history" in snapshot
        ws.send_text("ping")
        assert ws.receive_text() == "pong"


def test_dns_queries_websocket_ping(api_client):
    with api_client.websocket_connect("/dns-queries/ws") as ws:
        ws.send_text("ping")
        assert ws.receive_text() == "pong"
