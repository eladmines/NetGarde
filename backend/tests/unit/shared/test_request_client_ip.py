from typing import Dict, Optional

from app.shared.request_client_ip import client_ip_from_request, is_public_ip


class _Client:
    def __init__(self, host: str):
        self.host = host


class _Request:
    def __init__(self, *, host: str = "", headers: Optional[Dict[str, str]] = None):
        self.client = _Client(host) if host else None
        self.headers = headers or {}


def test_is_public_ip_rejects_private():
    assert is_public_ip("10.0.0.1") is False
    assert is_public_ip("192.168.1.1") is False


def test_is_public_ip_accepts_public():
    assert is_public_ip("8.8.8.8") is True


def test_client_ip_from_forwarded_for():
    req = _Request(
        headers={"X-Forwarded-For": "8.8.8.8, 10.0.0.1"},
    )
    assert client_ip_from_request(req) == "8.8.8.8"


def test_client_ip_from_client_host():
    req = _Request(host="1.1.1.1")
    assert client_ip_from_request(req) == "1.1.1.1"
