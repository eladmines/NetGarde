"""Evaluate time-based policy schedule rules."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List


def _parse_hhmm(value: str) -> int:
    """Minutes since midnight from 'HH:MM'."""
    parts = value.strip().split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    return hour * 60 + minute


def active_schedule_pack_slugs(rules: List[dict[str, Any]], now: datetime | None = None) -> List[str]:
    """
    Return pack slugs that should be enforced now.
    Rule: {"days": [0-6], "start": "22:00", "end": "07:00", "pack_slugs": ["social"]}
    Monday=0 .. Sunday=6 (Python weekday).
    Overnight: start > end means window crosses midnight.
    """
    if not rules:
        return []
    now = now or datetime.now(timezone.utc)
    weekday = now.weekday()
    minute_of_day = now.hour * 60 + now.minute
    active: List[str] = []

    for rule in rules:
        days = rule.get("days")
        if days is not None and weekday not in days:
            continue
        start = _parse_hhmm(str(rule.get("start", "00:00")))
        end = _parse_hhmm(str(rule.get("end", "23:59")))
        in_window = False
        if start <= end:
            in_window = start <= minute_of_day <= end
        else:
            in_window = minute_of_day >= start or minute_of_day <= end
        if in_window:
            for slug in rule.get("pack_slugs") or []:
                if slug not in active:
                    active.append(slug)
    return active
