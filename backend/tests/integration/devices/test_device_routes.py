def test_list_devices_empty(api_client):
    response = api_client.get("/devices")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_device(api_client, vpn_device):
    response = api_client.get("/devices")
    assert response.status_code == 200
    devices = response.json()
    assert len(devices) == 1
    assert devices[0]["id"] == vpn_device.id
    assert devices[0]["client_ip"] == "10.0.0.10"
    assert devices[0]["hostname"] == "test-laptop"


def test_create_device_via_api(api_client, db_session):
    from tests.helpers.factories import create_ip_lease

    lease = create_ip_lease(db_session, ip="10.0.0.20")

    response = api_client.post(
        "/devices",
        json={
            "ip_lease_id": lease.id,
            "hostname": "api-created",
            "mac_address": "11:22:33:44:55:66",
            "source": "manual",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["client_ip"] == "10.0.0.20"
    assert body["hostname"] == "api-created"


def test_get_device_login_locations_summary_empty(api_client):
    response = api_client.get("/devices/login-locations/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []


def test_assign_policy_profile_to_device(api_client, seed_policy, vpn_device):
    response = api_client.put(
        f"/devices/{vpn_device.id}/policy-assignment",
        json={"policy_profile_slug": "teen"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["device_id"] == vpn_device.id
    assert body["policy_profile_slug"] == "teen"
    assert body["in_quarantine"] is False
