import json

import pytest

from app.features.dashboard.services.llm_common import (
    bullets_look_like_metric_dump,
    compact_snapshot_for_llm,
    parse_bullets_from_content,
)


def test_detect_metric_dump_bullets():
    assert bullets_look_like_metric_dump(
        ["Peak mib/sec: 0.521", "Total alerts: 309", "Blocked attempts: 157"]
    )


def test_parse_json_bullets_object():
    raw = json.dumps(
        {
            "bullets": [
                "Traffic is quiet with one device online.",
                "Many sites were blocked in the last hour.",
            ]
        }
    )
    bullets = parse_bullets_from_content(raw)
    assert len(bullets) == 2
    assert "Traffic" in bullets[0]


def test_metric_dump_lines_raise():
    with pytest.raises(ValueError, match="metric labels"):
        parse_bullets_from_content("Peak mib/sec: 0.5\nTotal alerts: 10")


def test_compact_snapshot_trims_top_domains():
    compact = compact_snapshot_for_llm(
        {
            "period_minutes": 60,
            "blocked": {
                "count": 10,
                "top_domains": [
                    {"domain": "a.com", "count": 5},
                    {"domain": "b.com", "count": 4},
                    {"domain": "c.com", "count": 3},
                    {"domain": "d.com", "count": 2},
                ],
            },
            "alerts": {"total": 1, "by_type": {"x": 1}},
            "live": {},
            "history": {},
            "policy": {},
            "behavior": {},
        }
    )
    assert len(compact["blocked"]["top_domains"]) == 3
