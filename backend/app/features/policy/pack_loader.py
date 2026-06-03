"""Load curated domain list packs (static files + optional remote snapshots)."""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, List, Set

from app.features.policy.pack_common import BUILTIN_PACK_SLUGS, DATA_DIR, REMOTE_PACK_SLUGS, normalize_domain
from app.features.policy.pack_fetch import load_remote_or_static_pack, refresh_remote_pack


def clear_pack_cache() -> None:
    load_all_packs.cache_clear()


@lru_cache(maxsize=1)
def load_all_packs() -> Dict[str, frozenset[str]]:
    packs: Dict[str, frozenset[str]] = {}
    for slug in BUILTIN_PACK_SLUGS:
        if slug in REMOTE_PACK_SLUGS:
            packs[slug] = load_remote_or_static_pack(slug)
            continue
        path = DATA_DIR / f"{slug}.txt"
        if not path.exists():
            packs[slug] = frozenset()
            continue
        domains: Set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            normalized = normalize_domain(line)
            if normalized:
                domains.add(normalized)
        packs[slug] = frozenset(domains)
    return packs


def refresh_pack(slug: str) -> int:
    """Force-refresh a pack list; returns domain count."""
    if slug not in BUILTIN_PACK_SLUGS:
        raise ValueError(f"unknown pack slug: {slug}")
    if slug in REMOTE_PACK_SLUGS:
        count = len(refresh_remote_pack(slug, force=True))
    else:
        clear_pack_cache()
        return len(load_all_packs().get(slug, ()))
    clear_pack_cache()
    return count


def domains_for_packs(slugs: List[str]) -> Set[str]:
    all_packs = load_all_packs()
    out: Set[str] = set()
    for slug in slugs:
        out.update(all_packs.get(slug, ()))
    return out
