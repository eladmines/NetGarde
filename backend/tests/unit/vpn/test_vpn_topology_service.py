from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.features.vpn.services.vpn_topology_service import (
    VpnTopologyService,
    _handshake_status,
)
from tests.helpers.factories import create_vpn_device


def test_handshake_status_connected():
    now = int(datetime.now(timezone.utc).timestamp())
    assert _handshake_status(now - 30) == "connected"


def test_handshake_status_never():
    assert _handshake_status(0) == "never"


def test_handshake_status_idle():
    now = int(datetime.now(timezone.utc).timestamp())
    assert _handshake_status(now - 3600) == "idle"


@patch("app.features.vpn.services.vpn_topology_service.list_peers_on_host")
def test_get_topology(mock_list_peers, db_session, monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.VPN_POOL_NAME", "default")
    monkeypatch.setattr("app.shared.config.settings.VPN_ENDPOINT", "vpn.test:51820")
    monkeypatch.setattr("app.shared.config.settings.VPN_SERVER_PUBLIC_KEY", "serverKey=")
    monkeypatch.setattr("app.shared.config.settings.VPN_POOL_CIDR", "10.8.0.0/24")
    monkeypatch.setattr("app.shared.config.settings.VPN_GATEWAY_IP", "10.8.0.1")
    monkeypatch.setattr("app.shared.config.settings.VPN_DNS_IP", "10.8.0.1")

    device, _lease = create_vpn_device(db_session, ip="10.0.0.70", device_id="topo-dev")
    now = int(datetime.now(timezone.utc).timestamp())
    mock_list_peers.return_value = [
        {
            "public_key": "pubkey-topo-dev",
            "latest_handshake": now - 10,
            "endpoint": "1.2.3.4:51820",
            "rx_bytes": 1000,
            "tx_bytes": 2000,
        }
    ]

    svc = VpnTopologyService(db_session)
    topology = svc.get_topology()

    assert topology.server.endpoint == "vpn.test:51820"
    assert len(topology.peers) == 1
    assert topology.peers[0].device_id == device.id
    assert topology.peers[0].handshake_status == "connected"
    assert topology.peers[0].on_wireguard is True


def test_get_topology_no_pool_config(db_session, monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.VPN_ENDPOINT", "")
    monkeypatch.setattr("app.shared.config.settings.VPN_SERVER_PUBLIC_KEY", "")
    svc = VpnTopologyService(db_session)
    with pytest.raises(RuntimeError, match="VPN pool is not configured"):
        svc.get_topology()
