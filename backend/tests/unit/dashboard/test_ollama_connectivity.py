import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

from app.features.dashboard.services.ollama_connectivity import resolve_ollama_base_url


def test_resolve_ollama_tries_fallback_urls():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.side_effect = [
        Exception("connection refused"),
        mock_response,
    ]

    fake_httpx = ModuleType("httpx")
    fake_httpx.Client = MagicMock(return_value=mock_client)

    with patch("app.features.dashboard.services.ollama_connectivity.settings") as mock_settings:
        mock_settings.OLLAMA_BASE_URL = "http://ollama:11434"
        mock_settings.LLM_TIMEOUT_SEC = 30
        with patch.dict(sys.modules, {"httpx": fake_httpx}):
            base = resolve_ollama_base_url()

    assert base == "http://host.docker.internal:11434"
