from __future__ import annotations

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

BUILTIN_PACK_SLUGS = ("adult", "gambling", "malware", "social", "games")
# All built-in packs refresh from upstream lists (snapshot + static fallback).
REMOTE_PACK_SLUGS = frozenset(BUILTIN_PACK_SLUGS)


def normalize_domain(domain: str) -> str:
    d = domain.strip().lower()
    for prefix in ("https://", "http://", "www."):
        if d.startswith(prefix):
            d = d[len(prefix) :]
    d = d.split("/")[0].split("?")[0]
    return d
