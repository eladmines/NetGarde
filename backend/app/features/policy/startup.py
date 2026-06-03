"""Policy pack warmup on API startup."""

from __future__ import annotations

import logging

from app.features.policy.pack_common import REMOTE_PACK_SLUGS
from app.features.policy.pack_fetch import refresh_remote_pack
from app.shared.config import settings

log = logging.getLogger(__name__)


def warmup_policy_packs() -> None:
    if not settings.POLICY_PACK_FETCH_ENABLED or not settings.POLICY_PACK_REFRESH_ON_STARTUP:
        return
    for slug in REMOTE_PACK_SLUGS:
        try:
            domains = refresh_remote_pack(slug, force=False)
            log.info("policy pack %s ready (%d domains)", slug, len(domains))
        except Exception as e:
            log.warning("policy pack %s warmup failed: %s", slug, e)
