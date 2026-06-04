from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.features.policy.forbidden_country_rules import parse_forbidden_country_rules
from app.features.policy.schemas.policy import (
    AssignPolicyProfileRequest,
    DevicePolicyAssignmentRead,
    ForbiddenCountryPolicyRead,
    ForbiddenCountryRuleRead,
    PolicyApplyResponse,
    PolicyDnsSyncResponse,
    PolicyPackDomainsPage,
    PolicyPackRead,
    PolicyPackRefreshResponse,
    PolicyPackUpdate,
    PolicyProfileRead,
    PolicyProfileUpdate,
    PolicySyncReport,
    PolicySyncStatusRead,
)
from app.features.policy.services.policy_dns_service import PolicyDnsService
from app.features.policy.services.policy_service import PolicyService
from app.features.policy.services.vpn_login_geo_block_service import VpnLoginGeoBlockService
from app.shared.admin_auth import verify_admin_api_token
from app.shared.config import settings
from app.shared.dependencies import get_db
from app.shared.domain_country import country_display_name
from app.shared.service_auth import verify_dns_ingest_service

router = APIRouter(prefix="/policy", tags=["Policy"])


def get_policy_service(db: Session = Depends(get_db)) -> PolicyService:
    return PolicyService(db)


@router.get("/packs", response_model=list[PolicyPackRead])
def list_policy_packs(
    _: None = Depends(verify_admin_api_token),
    service: PolicyService = Depends(get_policy_service),
):
    return service.list_packs()


@router.get("/packs/{slug}/domains", response_model=PolicyPackDomainsPage)
def list_policy_pack_domains(
    slug: str,
    q: str = Query(default="", max_length=255),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    _: None = Depends(verify_admin_api_token),
    service: PolicyService = Depends(get_policy_service),
):
    """Paginated blocked-domain list for a pack (snapshot or seed file on server)."""
    return service.list_pack_domains(slug, q=q, skip=skip, limit=limit)


@router.post("/packs/{slug}/refresh", response_model=PolicyPackRefreshResponse)
def refresh_policy_pack(
    slug: str,
    _: None = Depends(verify_admin_api_token),
    service: PolicyService = Depends(get_policy_service),
):
    """Re-download upstream domain list for a built-in pack (social, adult, etc.)."""
    return service.refresh_pack_domains(slug)


@router.put("/packs/{slug}", response_model=PolicyPackRead)
def update_policy_pack(
    slug: str,
    body: PolicyPackUpdate,
    _: None = Depends(verify_admin_api_token),
    service: PolicyService = Depends(get_policy_service),
):
    return service.set_pack_enabled_globally(slug, body.enabled_globally)


@router.get("/profiles", response_model=list[PolicyProfileRead])
def list_policy_profiles(
    _: None = Depends(verify_admin_api_token),
    service: PolicyService = Depends(get_policy_service),
):
    return service.list_profiles()


@router.put("/profiles/{profile_id}", response_model=PolicyProfileRead)
def update_policy_profile(
    profile_id: int,
    body: PolicyProfileUpdate,
    _: None = Depends(verify_admin_api_token),
    service: PolicyService = Depends(get_policy_service),
):
    return service.update_profile(profile_id, body)


@router.get("/forbidden-countries", response_model=ForbiddenCountryPolicyRead)
def get_forbidden_country_policy(
    _: None = Depends(verify_admin_api_token),
):
    """How forbidden-country blocking selects the user country and which pairs are active."""
    rules = []
    for rule in parse_forbidden_country_rules():
        rules.append(
            ForbiddenCountryRuleRead(
                user_country=rule.user_country,
                user_country_name=country_display_name(rule.user_country),
                blocked_countries=list(rule.blocked_countries),
                blocked_country_names=[country_display_name(c) for c in rule.blocked_countries],
            )
        )
    blocked_login = VpnLoginGeoBlockService.blocked_login_countries()
    return ForbiddenCountryPolicyRead(
        enabled=bool(getattr(settings, "FORBIDDEN_COUNTRY_ENABLED", True)),
        user_country_source="vpn_login_geo",
        rules=rules,
        vpn_login_block_enabled=VpnLoginGeoBlockService.is_enabled(),
        blocked_vpn_login_countries=blocked_login,
        blocked_vpn_login_country_names=[country_display_name(c) for c in blocked_login],
    )


@router.get("/dns-sync", response_model=PolicyDnsSyncResponse)
def policy_dns_sync(
    _: None = Depends(verify_dns_ingest_service),
    db: Session = Depends(get_db),
):
    """Merged pack/profile/schedule/behavior blocks for dnsmasq (replaces blocked-sites sync)."""
    return PolicyDnsService(db).build_dns_sync()


@router.get("/sync-status", response_model=PolicySyncStatusRead)
def policy_sync_status(
    _: None = Depends(verify_admin_api_token),
    service: PolicyService = Depends(get_policy_service),
):
    return service.get_sync_status()


@router.post("/sync-report", response_model=PolicySyncStatusRead)
def policy_sync_report(
    body: PolicySyncReport,
    _: None = Depends(verify_dns_ingest_service),
    service: PolicyService = Depends(get_policy_service),
):
    """Called by dns-sync after writing dnsmasq config."""
    return service.record_sync_report(success=body.success, message=body.message)


@router.post("/apply", response_model=PolicyApplyResponse)
def apply_policy_now(
    _: None = Depends(verify_admin_api_token),
    service: PolicyService = Depends(get_policy_service),
):
    """Manually queue policy DNS sync + dnsmasq reload on the host listener."""
    return service.apply_policy_now()
