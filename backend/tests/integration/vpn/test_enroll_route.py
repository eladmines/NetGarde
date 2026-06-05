from unittest.mock import patch


@patch("app.features.vpn.services.enroll_service.apply_peer_on_host")
@patch("app.features.devices.services.device_login_geo_service.DeviceLoginGeoService.record_vpn_enroll")
def test_enroll_route_success(mock_geo, mock_wg, api_client, enroll_env, seed_policy):
    response = api_client.post(
        "/v1/enroll",
        json={
            "device_id": "route-client-1",
            "public_key": "routePubKey=",
            "hostname": "route-host",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["address"].endswith("/32")
    assert body["device_token"]
    assert body["endpoint"] == "vpn.test.example:51820"


@patch("app.features.vpn.services.enroll_service.apply_peer_on_host")
def test_enroll_route_conflict_returns_409(mock_wg, api_client, enroll_env, seed_policy):
    api_client.post(
        "/v1/enroll",
        json={"device_id": "dup-device", "public_key": "key-one="},
    )
    response = api_client.post(
        "/v1/enroll",
        json={"device_id": "dup-device", "public_key": "key-two="},
    )
    assert response.status_code == 409
    assert "public key" in response.json()["detail"].lower()
