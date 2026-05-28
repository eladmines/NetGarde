"""Map profile behavior sensitivity to scoring thresholds."""

from app.shared.config import settings

SENSITIVITY_THRESHOLDS = {
    "low": 95,
    "medium": 85,
    "high": 70,
}


def alert_threshold_for_sensitivity(sensitivity: str) -> int:
    key = (sensitivity or "medium").lower()
    if key == "low":
        return max(settings.BEHAVIOR_ALERT_THRESHOLD, 80)
    if key == "high":
        return min(settings.BEHAVIOR_ALERT_THRESHOLD, 65)
    return settings.BEHAVIOR_ALERT_THRESHOLD


def block_threshold_for_sensitivity(sensitivity: str) -> int:
    key = (sensitivity or "medium").lower()
    return SENSITIVITY_THRESHOLDS.get(key, settings.BEHAVIOR_AUTO_BLOCK_THRESHOLD)
