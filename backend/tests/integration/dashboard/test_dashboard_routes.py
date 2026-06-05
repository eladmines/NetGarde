from unittest.mock import patch


@patch("app.features.vpn.services.usage_service.UsageService.list_usage_history")
@patch("app.features.vpn.services.usage_service.UsageService.list_live_bandwidth")
def test_network_overview_route(mock_live, mock_history, api_client, dashboard_env, seed_policy):
    from datetime import datetime, timezone

    from app.features.vpn.schemas.usage_history import UsageHistoryPoint, UsageHistoryResponse
    from app.features.vpn.schemas.usage_live import DeviceUsageLiveResponse

    mock_live.return_value = DeviceUsageLiveResponse(items=[], max_age_sec=60)
    mock_history.return_value = UsageHistoryResponse(
        points=[
            UsageHistoryPoint(
                recorded_at=datetime.now(timezone.utc),
                rx_mib_per_sec=0.0,
                tx_mib_per_sec=0.0,
                total_mib_per_sec=0.0,
                reporting_clients=0,
            )
        ],
        minutes=60,
    )

    response = api_client.get("/dashboard/network-overview", params={"period_minutes": 60})
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "template"
    assert "bullets" in body
    assert "stats" in body
