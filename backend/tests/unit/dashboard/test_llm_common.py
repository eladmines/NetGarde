import json

import pytest

from app.features.dashboard.services.llm_common import parse_bullets_from_content


def test_parse_json_array():
    raw = json.dumps(["One bullet.", "Two bullet."])
    assert parse_bullets_from_content(raw) == ["One bullet.", "Two bullet."]


def test_parse_embedded_json_array():
    raw = 'Here is the summary:\n["Alert spike on social.", "Traffic normal."]'
    bullets = parse_bullets_from_content(raw)
    assert len(bullets) == 2
    assert "Alert spike" in bullets[0]


def test_parse_line_fallback():
    raw = "- First point\n- Second point"
    bullets = parse_bullets_from_content(raw)
    assert bullets[0] == "First point"
    assert bullets[1] == "Second point"


def test_parse_empty_raises():
    with pytest.raises(ValueError):
        parse_bullets_from_content("")
