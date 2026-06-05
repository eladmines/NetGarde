"""Reject VPN enroll when the client's public IP GeoIP is in a blocked login country."""

from __future__ import annotations

from typing import List, Optional

from app.shared.config import settings
from app.shared.domain_country import country_display_name
from app.shared.geoip import lookup_geo
from app.shared.request_client_ip import is_public_ip
from app.shared.logging_context import structured_extra
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class VpnLoginGeoBlockedError(ValueError):
    """Raised when enroll must be denied based on login country."""


class VpnLoginGeoBlockService:
    @staticmethod
    def is_enabled() -> bool:
        return bool(getattr(settings, "VPN_LOGIN_GEO_BLOCK_ENABLED", True))

    @staticmethod
    def blocked_login_countries() -> List[str]:
        raw = (getattr(settings, "BLOCKED_VPN_LOGIN_COUNTRIES", "") or "").strip()
        if not raw:
            return []
        if raw.startswith("["):
            import json

            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    return sorted(
                        {
                            str(c).strip().upper()
                            for c in data
                            if str(c).strip() and len(str(c).strip()) == 2
                        }
                    )
            except json.JSONDecodeError:
                pass
        return sorted(
            {
                part.strip().upper()
                for part in raw.split(",")
                if part.strip() and len(part.strip()) == 2
            }
        )

    @staticmethod
    def resolve_enroll_public_ip(
        connect_ip: Optional[str],
        client_reported_ip: Optional[str],
    ) -> Optional[str]:
        if client_reported_ip and is_public_ip(client_reported_ip.strip()):
            return client_reported_ip.strip()
        if connect_ip and is_public_ip(connect_ip.strip()):
            return connect_ip.strip()
        return None

    def lookup_login_country(
        self,
        connect_ip: Optional[str],
        client_reported_ip: Optional[str],
    ) -> Optional[str]:
        ip = self.resolve_enroll_public_ip(connect_ip, client_reported_ip)
        if not ip:
            return None
        geo = lookup_geo(ip)
        if geo and geo.country_code:
            return geo.country_code.strip().upper()
        return None

    def assert_enroll_allowed(
        self,
        *,
        connect_ip: Optional[str],
        client_reported_ip: Optional[str],
    ) -> None:
        """
        Fail closed only when GeoIP identifies a blocked login country.

        Unknown location (no public IP or lookup miss) is allowed so home users
        behind odd NAT are not locked out.
        """
        if not self.is_enabled():
            return

        blocked = self.blocked_login_countries()
        if not blocked:
            return

        country = self.lookup_login_country(connect_ip, client_reported_ip)
        if not country or country not in blocked:
            return

        name = country_display_name(country)
        ip = self.resolve_enroll_public_ip(connect_ip, client_reported_ip) or "unknown"
        logger.warning(
            "VPN enroll denied: blocked login country",
            extra=structured_extra(
                "enroll_geo_blocked",
                country_code=country,
                public_ip=ip,
            ),
        )
        raise VpnLoginGeoBlockedError(
            f"VPN enrollment is not allowed from {name} ({country}). "
            "Contact your network administrator if you believe this is an error."
        )
