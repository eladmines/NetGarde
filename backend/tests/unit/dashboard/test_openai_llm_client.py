import json
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

from app.features.dashboard.services.openai_llm_client import summarize_network_review


def test_openai_summarize_parses_response():
    snapshot = {"period_minutes": 60, "alerts": {"total": 1, "by_type": {}}}
    bullets_json = json.dumps(["Network is quiet.", "One alert in the last hour."])
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": bullets_json}}],
    }
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_response

    fake_httpx = ModuleType("httpx")
    fake_httpx.Client = MagicMock(return_value=mock_client)

    with patch("app.features.dashboard.services.openai_llm_client.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-4o-mini"
        mock_settings.OPENAI_BASE_URL = "https://api.openai.com/v1"
        mock_settings.LLM_TIMEOUT_SEC = 30
        with patch.dict(sys.modules, {"httpx": fake_httpx}):
            bullets = summarize_network_review(snapshot)

    assert bullets == ["Network is quiet.", "One alert in the last hour."]
    mock_client.post.assert_called_once()
