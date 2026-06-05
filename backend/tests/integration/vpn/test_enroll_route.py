def test_enroll_route_success(
    api_client,
    enroll_env,
    seed_policy,
    mock_apply_peer_on_host,
    mock_record_vpn_enroll,
    enroll_device,
):
    response = enroll_device(
        device_id="route-client-1",
        public_key="routePubKey=",
        hostname="route-host",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["address"].endswith("/32")
    assert body["device_token"]
    assert body["endpoint"] == "vpn.test.example:51820"


def test_enroll_route_conflict_returns_409(
    api_client,
    enroll_env,
    seed_policy,
    mock_apply_peer_on_host,
    enroll_device,
):
    enroll_device(device_id="dup-device", public_key="key-one=")
    response = enroll_device(device_id="dup-device", public_key="key-two=")
    assert response.status_code == 409
    assert "public key" in response.json()["detail"].lower()
