import pytest
from fastapi import HTTPException

from app.shared.admin_auth import verify_admin_api_token


def test_admin_auth_disabled_when_token_empty(monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.ADMIN_API_TOKEN", "")
    verify_admin_api_token(authorization=None)


def test_admin_auth_requires_bearer(monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.ADMIN_API_TOKEN", "secret-token")
    with pytest.raises(HTTPException) as exc:
        verify_admin_api_token(authorization=None)
    assert exc.value.status_code == 401


def test_admin_auth_rejects_invalid_token(monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.ADMIN_API_TOKEN", "secret-token")
    with pytest.raises(HTTPException) as exc:
        verify_admin_api_token(authorization="Bearer wrong-token")
    assert exc.value.status_code == 403


def test_admin_auth_accepts_valid_token(monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.ADMIN_API_TOKEN", "secret-token")
    verify_admin_api_token(authorization="Bearer secret-token")
