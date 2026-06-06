from unittest.mock import patch

import pytest

from app.features.devices.models.device import Device
from app.features.vpn.models.vpn_enroll_event import VpnEnrollEvent
from app.features.vpn.models.vpn_peer import VpnPeer
from app.features.vpn.schemas.enroll import EnrollRequest
from app.features.vpn.services.enroll_service import EnrollService
from tests.helpers.factories import seed_policy_catalog


@patch("app.features.vpn.services.enroll_service.apply_peer_on_host")
@patch("app.features.devices.services.device_login_geo_service.DeviceLoginGeoService.record_vpn_enroll")
def test_enroll_creates_peer_lease_and_device(mock_geo, mock_wg, db_session, enroll_env, seed_policy):
    svc = EnrollService(db_session)
    result = svc.enroll(
        EnrollRequest(
            device_id="laptop-01",
            public_key="clientPubKeyA=",
            hostname="work-laptop",
            mac_address="aa:bb:cc:dd:ee:01",
        ),
        connect_ip="203.0.113.10",
    )

    assert result["address"].endswith("/32")
    assert result["device_token"]
    assert result["endpoint"] == "vpn.test.example:51820"
    mock_wg.assert_called_once()
    mock_geo.assert_called_once()

    peer = db_session.query(VpnPeer).filter(VpnPeer.device_id == "laptop-01").one()
    device = db_session.query(Device).filter(Device.ip_lease_id.isnot(None)).one()
    assert device.hostname == "work-laptop"
    assert db_session.query(VpnEnrollEvent).filter(VpnEnrollEvent.peer_id == peer.id).count() == 1


@patch("app.features.vpn.services.enroll_service.apply_peer_on_host")
def test_enroll_reuses_device_when_mac_already_registered(mock_wg, db_session, enroll_env, seed_policy):
    svc = EnrollService(db_session)
    svc.enroll(
        EnrollRequest(
            device_id="device-a",
            public_key="clientPubKeyA=",
            mac_address="aa:bb:cc:dd:ee:01",
        )
    )

    result = svc.enroll(
        EnrollRequest(
            device_id="device-b",
            public_key="clientPubKeyB=",
            mac_address="aa:bb:cc:dd:ee:01",
        )
    )

    assert result["device_token"]
    devices = db_session.query(Device).filter(Device.mac_address == "aa:bb:cc:dd:ee:01").all()
    assert len(devices) == 1
    assert mock_wg.call_count == 2


@patch("app.features.vpn.services.enroll_service.apply_peer_on_host")
def test_enroll_rejects_conflicting_public_key(mock_wg, db_session, enroll_env, seed_policy):
    svc = EnrollService(db_session)
    svc.enroll(EnrollRequest(device_id="device-a", public_key="sameKey="))

    with pytest.raises(ValueError, match="different public key"):
        svc.enroll(EnrollRequest(device_id="device-a", public_key="otherKey="))

    mock_wg.assert_called_once()
