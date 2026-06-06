from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.features.policy.models.geo_country_block import (
    BLOCK_TYPE_DESTINATION,
    BLOCK_TYPE_VPN_LOGIN_DENY,
    GeoCountryBlock,
    GeoCountryPolicyConfig,
)


class GeoCountryBlockRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_config(self) -> GeoCountryPolicyConfig:
        row = self.db.query(GeoCountryPolicyConfig).filter(GeoCountryPolicyConfig.id == 1).first()
        if row is None:
            row = GeoCountryPolicyConfig(id=1)
            self.db.add(row)
            self.db.flush()
        return row

    def list_active(self, block_type: str) -> List[GeoCountryBlock]:
        return (
            self.db.query(GeoCountryBlock)
            .filter(GeoCountryBlock.block_type == block_type, GeoCountryBlock.is_active.is_(True))
            .order_by(GeoCountryBlock.country_code)
            .all()
        )

    def has_any_active(self) -> bool:
        return self.db.query(GeoCountryBlock.id).filter(GeoCountryBlock.is_active.is_(True)).first() is not None

    def is_configured_in_ui(self) -> bool:
        cfg = self.db.query(GeoCountryPolicyConfig).filter(GeoCountryPolicyConfig.id == 1).first()
        return bool(cfg and cfg.configured_in_ui)

    def replace_all(
        self,
        *,
        vpn_login_block_enabled: bool,
        destination_rules_enabled: bool,
        vpn_login_denied: List[str],
        destination_pairs: List[tuple[str, str]],
    ) -> None:
        cfg = self.get_config()
        cfg.configured_in_ui = True
        cfg.vpn_login_block_enabled = vpn_login_block_enabled
        cfg.destination_rules_enabled = destination_rules_enabled

        self.db.query(GeoCountryBlock).delete()
        for code in vpn_login_denied:
            self.db.add(
                GeoCountryBlock(
                    block_type=BLOCK_TYPE_VPN_LOGIN_DENY,
                    user_country_code=None,
                    country_code=code,
                    is_active=True,
                )
            )
        for user_cc, dest_cc in destination_pairs:
            self.db.add(
                GeoCountryBlock(
                    block_type=BLOCK_TYPE_DESTINATION,
                    user_country_code=user_cc,
                    country_code=dest_cc,
                    is_active=True,
                )
            )
        self.db.flush()

    def list_vpn_login_denied_codes(self) -> List[str]:
        return [r.country_code for r in self.list_active(BLOCK_TYPE_VPN_LOGIN_DENY)]

    def list_destination_pairs(self) -> List[tuple[str, str]]:
        rows = self.list_active(BLOCK_TYPE_DESTINATION)
        return [(r.user_country_code or "", r.country_code) for r in rows if r.user_country_code]
