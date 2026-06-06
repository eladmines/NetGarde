from typing import Optional

from app.features.client_behavior.schemas.behavior import BehaviorReviewRead
from app.shared.config import settings
from app.shared.redis_client import get_redis, redis_available

CACHE_PREFIX = "behavior:review:v1"


def _cache_key(device_id: int) -> str:
    mode = settings.BEHAVIOR_REVIEW_MODE.strip().lower()
    return f"{CACHE_PREFIX}:{device_id}:{mode}"


def get_cached_review(device_id: int) -> Optional[BehaviorReviewRead]:
    if not redis_available():
        return None
    try:
        raw = get_redis().get(_cache_key(device_id))
        if not raw:
            return None
        return BehaviorReviewRead.model_validate_json(raw)
    except Exception:
        return None


def set_cached_review(review: BehaviorReviewRead, device_id: int) -> None:
    if not redis_available():
        return
    ttl = max(30, int(settings.BEHAVIOR_REVIEW_CACHE_TTL_SEC))
    try:
        get_redis().setex(_cache_key(device_id), ttl, review.model_dump_json())
    except Exception:
        pass


def delete_cached_review(device_id: int) -> None:
    if not redis_available():
        return
    try:
        get_redis().delete(_cache_key(device_id))
    except Exception:
        pass
