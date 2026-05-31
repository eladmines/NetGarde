from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.features.devices.schemas.device import DeviceCreate, DeviceUpdate, DhcpSyncRequest
from app.features.client_behavior.schemas.behavior import (
    BehaviorProfileRead,
    BehaviorRecomputeResult,
    BlockedClientsListResponse,
    ClientBlockSyncResponse,
    ClientBlockedDomainRead,
    DeviceSecurityPolicyRead,
    DeviceSecurityPolicyUpdate,
)
from app.features.client_behavior.services.client_behavior_api_service import ClientBehaviorApiService
from app.features.policy.schemas.policy import AssignPolicyProfileRequest, DevicePolicyAssignmentRead
from app.features.policy.services.policy_service import PolicyService
from app.features.devices.controllers.device_controller import (
    create_device_controller,
    get_devices_controller,
    update_device_controller,
    delete_device_controller,
    sync_dhcp_leases_controller,
)
from app.features.devices.dependencies import get_device_service
from app.features.devices.services.device_service_interface import IDeviceService
from app.shared.dependencies import get_db
from app.shared.admin_auth import verify_admin_api_token
from app.shared.service_auth import verify_dns_ingest_service

router = APIRouter(prefix="/devices", tags=["Devices"])


def get_client_behavior_service(db: Session = Depends(get_db)) -> ClientBehaviorApiService:
    return ClientBehaviorApiService(db)


def get_policy_service(db: Session = Depends(get_db)) -> PolicyService:
    return PolicyService(db)


@router.post("")
def create_device_endpoint(
    data: DeviceCreate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
    service: IDeviceService = Depends(get_device_service),
):
    return create_device_controller(data, db, service)


@router.get("")
def get_devices_endpoint(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
    service: IDeviceService = Depends(get_device_service),
):
    return get_devices_controller(db, service)


@router.put("/{device_id}")
def update_device_endpoint(
    device_id: int,
    data: DeviceUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
    service: IDeviceService = Depends(get_device_service),
):
    return update_device_controller(device_id, data, db, service)


@router.delete("/{device_id}")
def delete_device_endpoint(
    device_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
    service: IDeviceService = Depends(get_device_service),
):
    return delete_device_controller(device_id, db, service)


@router.post("/sync-dhcp")
def sync_dhcp_endpoint(
    payload: DhcpSyncRequest,
    db: Session = Depends(get_db),
    _: None = Depends(verify_dns_ingest_service),
    service: IDeviceService = Depends(get_device_service),
):
    """Bulk upsert devices from router DHCP lease records."""
    return sync_dhcp_leases_controller(payload, db, service)


@router.get("/client-blocks/sync", response_model=ClientBlockSyncResponse)
def client_blocks_sync_endpoint(
    _: None = Depends(verify_dns_ingest_service),
    db: Session = Depends(get_db),
):
    """Legacy alias; use GET /policy/dns-sync. Returns block domains only (no quarantine allowlist)."""
    from app.features.client_behavior.schemas.behavior import ClientBlockSyncEntry
    from app.features.policy.services.policy_dns_service import PolicyDnsService

    sync = PolicyDnsService(db).build_dns_sync()
    entries = [
        ClientBlockSyncEntry(
            device_id=e.device_id,
            mac_address=e.mac_address,
            tag=e.tag,
            domains=e.block_domains if not e.allowlist_only else e.allowlist_domains,
        )
        for e in sync.entries
    ]
    return ClientBlockSyncResponse(entries=entries)


@router.get("/blocked-clients", response_model=BlockedClientsListResponse)
def list_blocked_clients_endpoint(
    _: None = Depends(verify_admin_api_token),
    behavior: ClientBehaviorApiService = Depends(get_client_behavior_service),
):
    """Devices with active auto-blocks after abnormal behavior scores."""
    return behavior.list_blocked_clients()


@router.post("/recompute-behavior-baselines", response_model=BehaviorRecomputeResult)
def recompute_behavior_baselines_endpoint(
    _: None = Depends(verify_admin_api_token),
    behavior: ClientBehaviorApiService = Depends(get_client_behavior_service),
):
    updated = behavior.recompute_baselines()
    return BehaviorRecomputeResult(devices_updated=updated)


@router.get("/{device_id}/policy-assignment", response_model=DevicePolicyAssignmentRead)
def get_device_policy_assignment_endpoint(
    device_id: int,
    _: None = Depends(verify_admin_api_token),
    service: PolicyService = Depends(get_policy_service),
):
    return service.get_device_policy(device_id)


@router.put("/{device_id}/policy-assignment", response_model=DevicePolicyAssignmentRead)
def assign_device_policy_profile_endpoint(
    device_id: int,
    body: AssignPolicyProfileRequest,
    _: None = Depends(verify_admin_api_token),
    service: PolicyService = Depends(get_policy_service),
):
    return service.assign_profile_to_device(device_id, body.policy_profile_slug)


@router.get("/{device_id}/behavior-profile", response_model=BehaviorProfileRead)
def get_behavior_profile_endpoint(
    device_id: int,
    _: None = Depends(verify_admin_api_token),
    behavior: ClientBehaviorApiService = Depends(get_client_behavior_service),
):
    return behavior.get_behavior_profile(device_id)


@router.get("/{device_id}/behavior-events")
def get_behavior_events_endpoint(
    device_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: None = Depends(verify_admin_api_token),
    behavior: ClientBehaviorApiService = Depends(get_client_behavior_service),
):
    return behavior.get_behavior_events(device_id, page=page, page_size=page_size)


@router.get("/{device_id}/security-policy", response_model=DeviceSecurityPolicyRead)
def get_security_policy_endpoint(
    device_id: int,
    _: None = Depends(verify_admin_api_token),
    behavior: ClientBehaviorApiService = Depends(get_client_behavior_service),
):
    return behavior.get_security_policy(device_id)


@router.put("/{device_id}/security-policy", response_model=DeviceSecurityPolicyRead)
def update_security_policy_endpoint(
    device_id: int,
    data: DeviceSecurityPolicyUpdate,
    _: None = Depends(verify_admin_api_token),
    behavior: ClientBehaviorApiService = Depends(get_client_behavior_service),
):
    return behavior.update_security_policy(device_id, data)


@router.get("/{device_id}/client-blocks", response_model=list[ClientBlockedDomainRead])
def list_client_blocks_endpoint(
    device_id: int,
    _: None = Depends(verify_admin_api_token),
    behavior: ClientBehaviorApiService = Depends(get_client_behavior_service),
):
    return behavior.list_client_blocks(device_id)


@router.delete("/{device_id}/client-blocks/{block_id}")
def revoke_client_block_endpoint(
    device_id: int,
    block_id: int,
    _: None = Depends(verify_admin_api_token),
    behavior: ClientBehaviorApiService = Depends(get_client_behavior_service),
):
    return behavior.revoke_client_block(device_id, block_id)
