from app.features.client_behavior.services.behavior_review_templates import (
    build_device_review_template,
    explain_alert_message,
)


def test_explain_alert_message_parses_score_and_reasons():
    msg = "Behavior score 82: query volume 120 vs expected ~20; new root burst 15 in 15m"
    text = explain_alert_message(msg, domain="bad.xyz")
    assert "82" in text
    assert "higher" in text.lower() or "unusual" in text.lower()


def test_build_device_review_template_ready_profile():
    snapshot = {
        "device_label": "Kids iPad",
        "profile_ready": True,
        "last_score": 75,
        "window": {"minutes": 15, "query_count": 40, "new_roots": 5},
        "recent_alerts": [],
        "active_block_count": 0,
    }
    text = build_device_review_template(snapshot)
    assert "Kids iPad" in text
    assert "75" in text
