from tests.helpers.integration import usage_report_payload


def test_usage_report_route(
    api_client,
    enroll_env,
    seed_policy,
    mock_apply_peer_on_host,
    mock_record_vpn_enroll,
    mock_usage_redis_unavailable,
    enroll_device,
):
    enroll = enroll_device(device_id="usage-client", public_key="usageKey=")
    assert enroll.status_code == 200
    token = enroll.json()["device_token"]

    response = api_client.post(
        "/v1/usage",
        json=usage_report_payload(device_id="usage-client"),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["stored"] is True
    assert body["rate_mib_per_sec"] >= 0


def test_usage_report_wrong_device_id(
    api_client,
    enroll_env,
    seed_policy,
    mock_apply_peer_on_host,
    enroll_device,
):
    enroll = enroll_device(device_id="usage-client-2", public_key="usageKey2=")
    token = enroll.json()["device_token"]
    response = api_client.post(
        "/v1/usage",
        json=usage_report_payload(device_id="other-device"),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
