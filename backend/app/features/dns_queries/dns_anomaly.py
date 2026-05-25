"""Heuristics for suspicious DNS activity."""

from __future__ import annotations

import re
from typing import Set

from app.shared.domain_utils import extract_root_domain

SUSPICIOUS_TLDS: Set[str] = {
    ".ru",
    ".xyz",
    ".top",
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".gq",
    ".su",
    ".cn",
}

_ENTROPY_LABEL = re.compile(r"^[a-z0-9]{16,}$", re.IGNORECASE)


def is_suspicious_tld(root_domain: str) -> bool:
    root = root_domain.lower()
    return any(root.endswith(tld) for tld in SUSPICIOUS_TLDS)


def is_high_entropy_subdomain(domain: str) -> bool:
    labels = domain.lower().rstrip(".").split(".")
    if len(labels) < 2:
        return False
    first = labels[0]
    if len(first) >= 20:
        digit_ratio = sum(ch.isdigit() for ch in first) / len(first)
        if digit_ratio >= 0.25:
            return True
    if len(first) >= 16 and _ENTROPY_LABEL.match(first):
        return True
    return False


def is_suspicious_domain(domain: str) -> bool:
    root = extract_root_domain(domain)
    return is_suspicious_tld(root) or is_high_entropy_subdomain(domain)
