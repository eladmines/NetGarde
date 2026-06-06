from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.features.policy.schemas.policy import (
    AssignPolicyProfileRequest,
    CountryChoice,
    DevicePolicyAssignmentRead,
    ForbiddenCountryPolicyRead,
    GeoCountryPolicyUpdate,
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
from app.features.policy.services.geo_country_policy_service import GeoCountryPolicyService
from app.features.policy.services.policy_dns_service import PolicyDnsService
from app.features.policy.services.policy_service import PolicyService
from app.shared.admin_auth import verify_admin_api_token
from app.shared.dependencies import get_db
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


@router.get("/geo-countries/choices", response_model=list[CountryChoice])
def list_geo_country_choices(
    _: None = Depends(verify_admin_api_token),
):
    return GeoCountryPolicyService.list_country_choices()


@router.get("/forbidden-countries", response_model=ForbiddenCountryPolicyRead)
def get_forbidden_country_policy(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
):
    """Effective geo country policy (database overrides env when rules are saved in UI)."""
    return GeoCountryPolicyService(db).get_policy_read()


@router.put("/forbidden-countries", response_model=ForbiddenCountryPolicyRead)
def update_forbidden_country_policy(
    body: GeoCountryPolicyUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
):
    """Save manual country blocks; applies after policy DNS sync."""
    return GeoCountryPolicyService(db).save_policy(body)


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
    """Run host dns-sync (run-sync.sh via wg-agent) and reload dnsmasq."""
    return service.apply_policy_now()
