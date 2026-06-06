"""Load and save admin-managed geo country blocks (DB with env fallback)."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.features.policy.forbidden_country_rules import (
    ForbiddenCountryRule,
    blocked_countries_for_user,
    parse_forbidden_country_rules,
)
from app.features.policy.models.geo_country_block import BLOCK_TYPE_DESTINATION
from app.features.policy.repositories.geo_country_block_repository import GeoCountryBlockRepository
from app.features.policy.schemas.policy import (
    CountryChoice,
    DestinationCountryRuleUpdate,
    ForbiddenCountryPolicyRead,
    ForbiddenCountryRuleRead,
    GeoCountryPolicyUpdate,
)
from app.features.policy.services.vpn_login_geo_block_service import (
    VpnLoginGeoBlockedError,
    VpnLoginGeoBlockService,
)
from app.shared.config import settings
from app.shared.domain_country import COUNTRY_NAMES, country_display_name


def _normalize_code(code: str) -> Optional[str]:
    c = (code or "").strip().upper()
    if len(c) != 2 or c in ("GLOBAL", "UNKNOWN"):
        return None
    return c


def _env_vpn_login_denied() -> List[str]:
    return VpnLoginGeoBlockService.blocked_login_countries()


def _env_destination_rules() -> List[ForbiddenCountryRule]:
    return parse_forbidden_country_rules()


def _rules_from_pairs(pairs: List[Tuple[str, str]]) -> List[ForbiddenCountryRule]:
    by_user: Dict[str, List[str]] = {}
    for user_cc, dest_cc in pairs:
        user = _normalize_code(user_cc)
        dest = _normalize_code(dest_cc)
        if not user or not dest:
            continue
        by_user.setdefault(user, []).append(dest)
    return [
        ForbiddenCountryRule(user_country=user, blocked_countries=tuple(sorted(set(dests))))
        for user, dests in sorted(by_user.items())
    ]


class GeoCountryPolicyService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = GeoCountryBlockRepository(db)

    def uses_database(self) -> bool:
        return self.repo.is_configured_in_ui()

    def _use_db_policy(self) -> bool:
        return self.repo.is_configured_in_ui()

    def vpn_login_block_enabled(self) -> bool:
        if self._use_db_policy():
            return bool(self.repo.get_config().vpn_login_block_enabled)
        return VpnLoginGeoBlockService.is_enabled()

    def destination_rules_enabled(self) -> bool:
        if self._use_db_policy():
            return bool(self.repo.get_config().destination_rules_enabled)
        return bool(getattr(settings, "FORBIDDEN_COUNTRY_ENABLED", True))

    def vpn_login_denied_countries(self) -> List[str]:
        if self._use_db_policy():
            return self.repo.list_vpn_login_denied_codes()
        return _env_vpn_login_denied()

    def destination_rules(self) -> List[ForbiddenCountryRule]:
        if self._use_db_policy():
            return _rules_from_pairs(self.repo.list_destination_pairs())
        return _env_destination_rules()

    def blocked_destinations_for_user(self, user_country: str | None) -> List[str]:
        if not self.destination_rules_enabled():
            return []
        return blocked_countries_for_user(user_country, self.destination_rules())

    def get_policy_read(self) -> ForbiddenCountryPolicyRead:
        rules = self.destination_rules()
        denied = self.vpn_login_denied_countries()
        return ForbiddenCountryPolicyRead(
            enabled=self.destination_rules_enabled(),
            user_country_source="vpn_login_geo",
            rules=[
                ForbiddenCountryRuleRead(
                    user_country=r.user_country,
                    user_country_name=country_display_name(r.user_country),
                    blocked_countries=list(r.blocked_countries),
                    blocked_country_names=[country_display_name(c) for c in r.blocked_countries],
                )
                for r in rules
            ],
            vpn_login_block_enabled=self.vpn_login_block_enabled(),
            blocked_vpn_login_countries=denied,
            blocked_vpn_login_country_names=[country_display_name(c) for c in denied],
            managed_in_database=self.uses_database(),
        )

    def save_policy(self, body: GeoCountryPolicyUpdate) -> ForbiddenCountryPolicyRead:
        vpn_denied: List[str] = []
        for raw in body.vpn_login_denied_countries:
            c = _normalize_code(raw)
            if c:
                vpn_denied.append(c)

        pairs: List[tuple[str, str]] = []
        for rule in body.destination_rules:
            user = _normalize_code(rule.user_country)
            if not user:
                continue
            for raw_dest in rule.blocked_countries:
                dest = _normalize_code(raw_dest)
                if dest:
                    pairs.append((user, dest))

        self.repo.replace_all(
            vpn_login_block_enabled=body.vpn_login_block_enabled,
            destination_rules_enabled=body.destination_rules_enabled,
            vpn_login_denied=sorted(set(vpn_denied)),
            destination_pairs=pairs,
        )
        self.db.commit()
        return self.get_policy_read()

    def assert_vpn_enroll_allowed(
        self,
        *,
        connect_ip: Optional[str],
        client_reported_ip: Optional[str],
    ) -> None:
        if not self.vpn_login_block_enabled():
            return
        blocked = self.vpn_login_denied_countries()
        if not blocked:
            return
        country = VpnLoginGeoBlockService().lookup_login_country(connect_ip, client_reported_ip)
        if not country or country not in blocked:
            return
        name = country_display_name(country)
        raise VpnLoginGeoBlockedError(
            f"VPN enrollment is not allowed from {name} ({country}). "
            "Contact your network administrator if you believe this is an error."
        )

    @staticmethod
    def list_country_choices() -> List[CountryChoice]:
        items = [
            CountryChoice(code=code, name=name)
            for code, name in COUNTRY_NAMES.items()
            if code not in ("GLOBAL", "UNKNOWN") and len(code) == 2
        ]
        return sorted(items, key=lambda x: x.name)
