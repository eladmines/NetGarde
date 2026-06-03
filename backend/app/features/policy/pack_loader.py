"""Load curated domain list packs (static files + optional remote snapshots)."""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, List, Set

from app.features.policy.pack_common import BUILTIN_PACK_SLUGS, REMOTE_PACK_SLUGS
from app.features.policy.pack_fetch import (
    clear_sorted_pack_domains_cache,
    load_remote_or_static_pack,
    pack_domain_count_meta,
    refresh_remote_pack,
)


def clear_pack_cache() -> None:
    load_all_packs.cache_clear()
    clear_sorted_pack_domains_cache()


@lru_cache(maxsize=1)
def load_all_packs() -> Dict[str, frozenset[str]]:
    packs: Dict[str, frozenset[str]] = {}
    for slug in BUILTIN_PACK_SLUGS:
        packs[slug] = load_remote_or_static_pack(slug)
    return packs


def refresh_pack(slug: str) -> int:
    """Force-refresh a pack list; returns domain count."""
    if slug not in BUILTIN_PACK_SLUGS:
        raise ValueError(f"unknown pack slug: {slug}")
    if slug not in REMOTE_PACK_SLUGS:
        raise ValueError(f"pack {slug} is not refreshable")
    count = len(refresh_remote_pack(slug, force=True))
    clear_pack_cache()
    return count


def pack_domain_counts() -> Dict[str, int]:
    """Counts for admin API — never triggers upstream fetch."""
    return {slug: pack_domain_count_meta(slug)[0] for slug in BUILTIN_PACK_SLUGS}


def pack_domain_count_sources() -> Dict[str, str]:
    return {slug: pack_domain_count_meta(slug)[1] for slug in BUILTIN_PACK_SLUGS}


def domains_for_packs(slugs: List[str]) -> Set[str]:
    all_packs = load_all_packs()
    out: Set[str] = set()
    for slug in slugs:
        out.update(all_packs.get(slug, ()))
    return out
