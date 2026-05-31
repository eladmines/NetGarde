"""Load curated domain list packs from static files."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Set

DATA_DIR = Path(__file__).resolve().parent / "data"

BUILTIN_PACK_SLUGS = ("adult", "gambling", "malware", "social", "games")


def normalize_domain(domain: str) -> str:
    d = domain.strip().lower()
    for prefix in ("https://", "http://", "www."):
        if d.startswith(prefix):
            d = d[len(prefix) :]
    d = d.split("/")[0].split("?")[0]
    return d


@lru_cache(maxsize=1)
def load_all_packs() -> Dict[str, frozenset[str]]:
    packs: Dict[str, frozenset[str]] = {}
    for slug in BUILTIN_PACK_SLUGS:
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


def domains_for_packs(slugs: List[str]) -> Set[str]:
    all_packs = load_all_packs()
    out: Set[str] = set()
    for slug in slugs:
        out.update(all_packs.get(slug, ()))
    return out
