"""Rules-based parent-facing text for device behavior (no LLM)."""

from __future__ import annotations

import re
from typing import Any, List, Optional

_SCORE_RE = re.compile(r"Behavior score (\d+)", re.IGNORECASE)


def _device_label(snapshot: dict[str, Any]) -> str:
    return snapshot.get("device_label") or f"Device {snapshot.get('device_id', '')}"


def explain_alert_message(message: Optional[str], *, domain: Optional[str] = None) -> str:
    """Turn a technical behavior_anomaly message into plain language."""
    if not message or not message.strip():
        if domain:
            return f"Unusual activity was detected involving {domain}."
        return "Unusual activity was detected on this device."

    score_match = _SCORE_RE.search(message)
    score = int(score_match.group(1)) if score_match else None
    reasons_part = message
    if ":" in message:
        reasons_part = message.split(":", 1)[1].strip()
    if "(top domain:" in reasons_part:
        reasons_part = reasons_part.split("(top domain:")[0].strip().rstrip(";,")

    reasons: List[str] = [r.strip() for r in reasons_part.split(";") if r.strip()]
    if not reasons:
        reasons = [reasons_part] if reasons_part else []

    friendly: List[str] = []
    for r in reasons:
        low = r.lower()
        if "query volume" in low:
            friendly.append("DNS activity was much higher than this device usually has")
        elif "new root burst" in low:
            friendly.append("the device looked up many new websites in a short time")
        elif "unusual activity at hour" in low:
            friendly.append("activity happened at an unusual time of day for this device")
        elif "suspicious domain" in low:
            friendly.append(f"a suspicious domain was accessed ({r.split()[-1] if r.split() else 'unknown'})")
        else:
            friendly.append(r)

    joined = ", and ".join(friendly[:3])
    if score is not None:
        if score >= 85:
            opener = f"High-risk unusual activity (score {score})"
        elif score >= 70:
            opener = f"Notable unusual activity (score {score})"
        else:
            opener = f"Elevated activity (score {score})"
        return f"{opener}: {joined}." if joined else f"{opener}."
    return f"Unusual activity: {joined}." if joined else message


def build_device_review_template(snapshot: dict[str, Any]) -> str:
    """One paragraph summary for a device from metrics snapshot."""
    label = _device_label(snapshot)
    score = snapshot.get("last_score")
    ready = snapshot.get("profile_ready", False)
    window = snapshot.get("window") or {}
    alerts = snapshot.get("recent_alerts") or []
    blocks = int(snapshot.get("active_block_count") or 0)

    if not ready:
        return (
            f"{label} is still learning normal DNS patterns. "
            "After a few days of typical use, NetGarde can explain unusual activity more clearly."
        )

    parts: List[str] = []
    if score is None or score < 50:
        parts.append(f"{label} looks typical right now based on recent DNS patterns.")
    elif score < 70:
        parts.append(
            f"{label} shows slightly elevated activity (score {score}) but below your alert threshold."
        )
    else:
        parts.append(f"{label} shows unusual DNS activity (score {score}).")

    q = int(window.get("query_count") or 0)
    new_roots = int(window.get("new_roots") or 0)
    window_min = int(window.get("minutes") or 15)
    if q > 0:
        parts.append(
            f"In the last {window_min} minutes there were {q} DNS lookups"
            + (f" including {new_roots} new sites." if new_roots else ".")
        )

    if alerts:
        latest = alerts[0]
        parent = explain_alert_message(
            latest.get("message"),
            domain=latest.get("domain"),
        )
        parts.append(f"Latest alert: {parent}")

    if blocks > 0:
        parts.append(
            f"{blocks} domain(s) are temporarily blocked due to this behavior."
        )

    return " ".join(parts)
