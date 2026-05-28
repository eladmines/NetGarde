from datetime import datetime, timezone

from app.features.policy.schedule import active_schedule_pack_slugs


def test_schedule_overnight_window():
    rules = [
        {
            "days": [0, 1, 2, 3, 4, 5, 6],
            "start": "22:00",
            "end": "07:00",
            "pack_slugs": ["social", "games"],
        }
    ]
    at_night = datetime(2026, 5, 28, 23, 0, tzinfo=timezone.utc)
    at_day = datetime(2026, 5, 28, 12, 0, tzinfo=timezone.utc)
    assert "social" in active_schedule_pack_slugs(rules, at_night)
    assert active_schedule_pack_slugs(rules, at_day) == []
