"""Policy pack warmup on API startup."""

from __future__ import annotations

from app.features.policy.pack_common import REMOTE_PACK_SLUGS
from app.features.policy.pack_fetch import refresh_remote_pack
from app.shared.config import settings
from app.shared.logging_context import structured_extra
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


def warmup_policy_packs() -> None:
    if not settings.POLICY_PACK_FETCH_ENABLED or not settings.POLICY_PACK_REFRESH_ON_STARTUP:
        return
    for slug in REMOTE_PACK_SLUGS:
        try:
            domains = refresh_remote_pack(slug, force=False)
            logger.info(
                "Policy pack warmup ready",
                extra=structured_extra(
                    "policy_pack_warmup_ready",
                    slug=slug,
                    domain_count=len(domains),
                ),
            )
        except Exception as e:
            logger.warning(
                "Policy pack warmup failed",
                extra=structured_extra(
                    "policy_pack_warmup_failed",
                    slug=slug,
                    error=str(e),
                ),
            )
