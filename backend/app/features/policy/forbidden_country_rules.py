"""Parse admin-configured forbidden country pair rules (JSON)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

from app.shared.config import settings


@dataclass(frozen=True)
class ForbiddenCountryRule:
    """When user_country matches, block DNS for destination countries (ISO 3166-1 alpha-2)."""

    user_country: str
    blocked_countries: tuple[str, ...]


def parse_forbidden_country_rules(raw: str | None = None) -> List[ForbiddenCountryRule]:
    text = (raw if raw is not None else getattr(settings, "FORBIDDEN_COUNTRY_RULES", "") or "").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []

    rules: List[ForbiddenCountryRule] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        user = str(item.get("user_country") or "").strip().upper()
        blocked_raw = item.get("blocked_countries") or item.get("blocked_destination_countries") or []
        if not user or len(user) != 2:
            continue
        blocked: List[str] = []
        if isinstance(blocked_raw, list):
            for code in blocked_raw:
                c = str(code).strip().upper()
                if len(c) == 2 and c not in ("GLOBAL", "UNKNOWN"):
                    blocked.append(c)
        if blocked:
            rules.append(ForbiddenCountryRule(user_country=user, blocked_countries=tuple(sorted(set(blocked)))))
    return rules


def blocked_countries_for_user(user_country: str | None, rules: List[ForbiddenCountryRule] | None = None) -> List[str]:
    if not user_country:
        return []
    code = user_country.strip().upper()
    if len(code) != 2:
        return []
    rules = rules if rules is not None else parse_forbidden_country_rules()
    out: List[str] = []
    for rule in rules:
        if rule.user_country == code:
            out.extend(rule.blocked_countries)
    return sorted(set(out))
