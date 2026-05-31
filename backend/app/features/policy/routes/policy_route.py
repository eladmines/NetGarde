from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.features.policy.schemas.policy import (
    AssignPolicyProfileRequest,
    DevicePolicyAssignmentRead,
    PolicyApplyResponse,
    PolicyDnsSyncResponse,
    PolicyPackRead,
    PolicyPackUpdate,
    PolicyProfileRead,
    PolicyProfileUpdate,
    PolicySyncReport,
    PolicySyncStatusRead,
)
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
