from unittest.mock import patch


@patch("app.features.vpn.services.enroll_service.apply_peer_on_host")
@patch("app.features.devices.services.device_login_geo_service.DeviceLoginGeoService.record_vpn_enroll")
def test_usage_report_route(mock_geo, mock_wg, api_client, enroll_env, seed_policy):
    enroll = api_client.post(
        "/v1/enroll",
        json={"device_id": "usage-client", "public_key": "usageKey="},
    )
    assert enroll.status_code == 200
    token = enroll.json()["device_token"]

    with patch("app.features.vpn.services.usage_service.redis_available", return_value=False):
        response = api_client.post(
            "/v1/usage",
            json={
                "device_id": "usage-client",
                "interval_sec": 5.0,
                "rx_bytes": 1000,
                "tx_bytes": 500,
                "delta_rx_bytes": 1000,
                "delta_tx_bytes": 500,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["stored"] is True
    assert body["rate_mib_per_sec"] >= 0


@patch("app.features.vpn.services.enroll_service.apply_peer_on_host")
def test_usage_report_wrong_device_id(mock_wg, api_client, enroll_env, seed_policy):
    enroll = api_client.post(
        "/v1/enroll",
        json={"device_id": "usage-client-2", "public_key": "usageKey2="},
    )
    token = enroll.json()["device_token"]
    response = api_client.post(
        "/v1/usage",
        json={
            "device_id": "other-device",
            "interval_sec": 5.0,
            "rx_bytes": 0,
            "tx_bytes": 0,
            "delta_rx_bytes": 0,
            "delta_tx_bytes": 0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
