import json
from typing import Optional

from app.features.dashboard.schemas.network_overview import NetworkOverviewRead
from app.shared.config import settings
from app.shared.redis_client import get_redis, redis_available

CACHE_PREFIX = "dashboard:network_overview:v1"


def _cache_key(period_minutes: int) -> str:
    mode = settings.NETWORK_REVIEW_MODE.strip().lower()
    return f"{CACHE_PREFIX}:{period_minutes}:{mode}"


def get_cached_overview(period_minutes: int) -> Optional[NetworkOverviewRead]:
    if not redis_available():
        return None
    try:
        raw = get_redis().get(_cache_key(period_minutes))
        if not raw:
            return None
        return NetworkOverviewRead.model_validate_json(raw)
    except Exception:
        return None


def set_cached_overview(overview: NetworkOverviewRead, period_minutes: int) -> None:
    if not redis_available():
        return
    ttl = max(15, int(settings.NETWORK_REVIEW_CACHE_TTL_SEC))
    try:
        get_redis().setex(
            _cache_key(period_minutes),
            ttl,
            overview.model_dump_json(),
        )
    except Exception:
        pass


def delete_cached_overview(period_minutes: int) -> None:
    if not redis_available():
        return
    try:
        get_redis().delete(_cache_key(period_minutes))
    except Exception:
        pass
