import { getAdminAuthHeaders } from '../../../shared/utils/authHeaders';
import { DnsAlertListResponse } from '../../dns-queries/types/dnsQuery';
import {
  Device,
  BehaviorProfile,
  DeviceSecurityPolicy,
  ClientBlockedDomain,
  BlockedClientsListResponse,
} from '../types/device';
import { DevicePolicyAssignment } from '../../policy/types/policy';
import { DeviceUsageLiveResponse } from '../../dashboard/types/usageLive';

import { API_BASE_URL } from '../../../shared/config/apiBaseUrl';

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...getAdminAuthHeaders(),
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const devicesApi = {
  list: () => apiFetch<Device[]>('/devices'),
  listUsageLive: (maxAgeSec?: number) => {
    const q = maxAgeSec != null ? `?max_age_sec=${maxAgeSec}` : '';
    return apiFetch<DeviceUsageLiveResponse>(`/devices/usage/live${q}`);
  },
  listBlockedClients: () => apiFetch<BlockedClientsListResponse>('/devices/blocked-clients'),
  getPolicyAssignment: (deviceId: number) =>
    apiFetch<DevicePolicyAssignment>(`/devices/${deviceId}/policy-assignment`),
  assignPolicyProfile: (deviceId: number, policy_profile_slug: string) =>
    apiFetch<DevicePolicyAssignment>(`/devices/${deviceId}/policy-assignment`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ policy_profile_slug }),
    }),
  getBehaviorProfile: (deviceId: number) =>
    apiFetch<BehaviorProfile>(`/devices/${deviceId}/behavior-profile`),
  getSecurityPolicy: (deviceId: number) =>
    apiFetch<DeviceSecurityPolicy>(`/devices/${deviceId}/security-policy`),
  updateSecurityPolicy: (deviceId: number, body: Partial<DeviceSecurityPolicy>) =>
    apiFetch<DeviceSecurityPolicy>(`/devices/${deviceId}/security-policy`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  listClientBlocks: (deviceId: number) =>
    apiFetch<ClientBlockedDomain[]>(`/devices/${deviceId}/client-blocks`),
  revokeClientBlock: (deviceId: number, blockId: number) =>
    apiFetch<{ revoked: boolean }>(`/devices/${deviceId}/client-blocks/${blockId}`, {
      method: 'DELETE',
    }),
  getBehaviorEvents: (deviceId: number, page = 1, pageSize = 20) =>
    apiFetch<DnsAlertListResponse>(
      `/devices/${deviceId}/behavior-events?page=${page}&page_size=${pageSize}`,
    ),
};
