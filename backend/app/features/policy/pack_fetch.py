"""Fetch curated pack lists from upstream hosts files and cache on disk."""

from __future__ import annotations

import logging
import time
import urllib.error
import urllib.request
from pathlib import Path
from functools import lru_cache
from typing import FrozenSet, List, Optional, Set, Tuple

from app.features.policy.pack_common import DATA_DIR, normalize_domain
from app.shared.config import settings

log = logging.getLogger(__name__)

SNAPSHOT_DIR = DATA_DIR / "snapshots"

# StevenBlack extension data lives under per-source subfolders (e.g. sinfonietta/).
_STEVENBLACK = "https://raw.githubusercontent.com/StevenBlack/hosts/master"
DEFAULT_REMOTE_PACK_URLS: dict[str, str] = {
    "social": f"{_STEVENBLACK}/extensions/social/sinfonietta/hosts",
    "adult": f"{_STEVENBLACK}/extensions/porn/sinfonietta/hosts",
    "gambling": f"{_STEVENBLACK}/extensions/gambling/sinfonietta/hosts",
    "malware": f"{_STEVENBLACK}/hosts",
    "games": "https://raw.githubusercontent.com/olbat/ut1-blacklists/master/blacklists/games/domains",
}

_HOSTS_BLOCK_IPS = frozenset({"0.0.0.0", "127.0.0.1", "::", "::1", "0.0.0.0"})


def parse_hosts_file(text: str) -> Set[str]:
    domains: Set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        if parts[0] not in _HOSTS_BLOCK_IPS:
            continue
        d = normalize_domain(parts[-1])
        if d and "." in d:
            domains.add(d)
    return domains


def parse_domain_list(text: str) -> Set[str]:
    """Plain-text lists with one domain per line (e.g. UT1 blacklists)."""
    domains: Set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        d = normalize_domain(line.split()[0])
        if d and "." in d:
            domains.add(d)
    return domains


def parse_pack_text(text: str) -> Set[str]:
    """Hosts file format first; fall back to plain domain-per-line."""
    from_hosts = parse_hosts_file(text)
    if from_hosts:
        return from_hosts
    return parse_domain_list(text)


def snapshot_path(slug: str) -> Path:
    return SNAPSHOT_DIR / f"{slug}.txt"


def _read_domains_file(path: Path) -> Set[str]:
    domains: Set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        d = normalize_domain(line)
        if d:
            domains.add(d)
    return domains


def write_snapshot(slug: str, domains: Set[str]) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = snapshot_path(slug)
    body = "\n".join(sorted(domains)) + ("\n" if domains else "")
    path.write_text(body, encoding="utf-8")
    return path


def snapshot_age_seconds(slug: str) -> Optional[float]:
    path = snapshot_path(slug)
    if not path.is_file():
        return None
    return time.time() - path.stat().st_mtime


def fetch_remote_hosts(url: str, timeout: float) -> Set[str]:
    req = urllib.request.Request(url, headers={"User-Agent": "NetGarde-PolicyPack/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    domains = parse_pack_text(text)
    if not domains:
        raise ValueError(f"no domains parsed from {url}")
    return domains


def remote_pack_url(slug: str) -> Optional[str]:
    if not settings.POLICY_PACK_FETCH_ENABLED:
        return None
    override = settings.policy_pack_remote_urls.get(slug)
    if override:
        return override.strip()
    return DEFAULT_REMOTE_PACK_URLS.get(slug)


def refresh_remote_pack(slug: str, *, force: bool = False) -> FrozenSet[str]:
    """Download upstream list, write snapshot, return domains."""
    url = remote_pack_url(slug)
    if not url:
        raise ValueError(f"pack {slug!r} has no remote source or fetch is disabled")

    if not force:
        age = snapshot_age_seconds(slug)
        if age is not None and age < settings.POLICY_PACK_SNAPSHOT_MAX_AGE_SECONDS:
            domains = _read_domains_file(snapshot_path(slug))
            if domains:
                return frozenset(domains)

    static_fallback = DATA_DIR / f"{slug}.txt"
    try:
        domains = fetch_remote_hosts(url, settings.POLICY_PACK_FETCH_TIMEOUT_SECONDS)
        write_snapshot(slug, domains)
        log.info("refreshed policy pack %s from %s (%d domains)", slug, url, len(domains))
        clear_sorted_pack_domains_cache()
        return frozenset(domains)
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        log.warning("failed to fetch policy pack %s from %s: %s", slug, url, e)
        snap = snapshot_path(slug)
        if snap.is_file():
            domains = _read_domains_file(snap)
            if domains:
                log.info("using stale snapshot for pack %s (%d domains)", slug, len(domains))
                return frozenset(domains)
        if static_fallback.is_file():
            domains = _read_domains_file(static_fallback)
            log.info("using static fallback for pack %s (%d domains)", slug, len(domains))
            return frozenset(domains)
        raise


def load_cached_pack(slug: str) -> FrozenSet[str]:
    """Load domains from on-disk snapshot or bundled static file (no network I/O)."""
    snap = snapshot_path(slug)
    if snap.is_file():
        domains = _read_domains_file(snap)
        if domains:
            return frozenset(domains)
    static = DATA_DIR / f"{slug}.txt"
    if static.is_file():
        return frozenset(_read_domains_file(static))
    return frozenset()


def count_cached_pack_domains(slug: str) -> int:
    """Domain count for API display without loading full packs into memory."""
    count, _ = pack_domain_count_meta(slug)
    return count


def pack_domain_count_meta(slug: str) -> tuple[int, str]:
    """
    Return (count, source).
    source is 'snapshot' (downloaded upstream list), 'seed' (bundled fallback), or 'empty'.
    """
    snap = snapshot_path(slug)
    if snap.is_file():
        snap_count = len(_read_domains_file(snap))
        if snap_count > 0:
            return snap_count, "snapshot"
    static = DATA_DIR / f"{slug}.txt"
    if static.is_file():
        seed_count = len(_read_domains_file(static))
        if seed_count > 0:
            return seed_count, "seed"
    return 0, "empty"


def clear_sorted_pack_domains_cache() -> None:
    _sorted_pack_domains.cache_clear()


@lru_cache(maxsize=16)
def _sorted_pack_domains(slug: str) -> Tuple[str, ...]:
    return tuple(sorted(load_cached_pack(slug)))


def list_pack_domains_page(
    slug: str,
    *,
    q: str = "",
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[str], int, str]:
    """Paginated domain list for admin UI (search is substring match)."""
    _, source = pack_domain_count_meta(slug)
    domains = list(_sorted_pack_domains(slug))
    query = q.strip().lower()
    if query:
        domains = [d for d in domains if query in d]
    total = len(domains)
    page = domains[max(0, skip) : max(0, skip) + limit]
    return page, total, source


def load_remote_or_static_pack(slug: str) -> FrozenSet[str]:
    """DNS sync path: prefer cache; refresh from network only if cache is empty."""
    cached = load_cached_pack(slug)
    if cached:
        return cached
    if remote_pack_url(slug):
        try:
            return refresh_remote_pack(slug, force=False)
        except Exception:
            log.warning("pack %s refresh failed during load; using empty set", slug)
    return frozenset()
