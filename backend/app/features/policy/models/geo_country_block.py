from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint

from app.shared.database import Base

BLOCK_TYPE_VPN_LOGIN_DENY = "vpn_login_deny"
BLOCK_TYPE_DESTINATION = "destination_block"


class GeoCountryBlock(Base):
    """Admin-managed country blocks (VPN enroll deny or destination DNS by user country)."""

    __tablename__ = "geo_country_blocks"

    id = Column(Integer, primary_key=True, index=True)
    block_type = Column(String(32), nullable=False, index=True)
    user_country_code = Column(String(2), nullable=True, index=True)
    country_code = Column(String(2), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "block_type",
            "user_country_code",
            "country_code",
            name="uq_geo_country_blocks_type_user_dest",
        ),
    )


class GeoCountryPolicyConfig(Base):
    """Singleton toggles for geo country policies (row id=1)."""

    __tablename__ = "geo_country_policy_config"

    id = Column(Integer, primary_key=True)
    configured_in_ui = Column(Boolean, nullable=False, default=False)
    vpn_login_block_enabled = Column(Boolean, nullable=False, default=True)
    destination_rules_enabled = Column(Boolean, nullable=False, default=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
