import { getAdminAuthHeaders } from '../../../shared/utils/authHeaders';
import { API_BASE_URL } from '../../../shared/config/apiBaseUrl';
import { DevicePolicyAssignment, PolicyApplyResult, PolicyPack, PolicyProfile, PolicySyncStatus } from '../types/policy';

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

export const policyApi = {
  listPacks: () => apiFetch<PolicyPack[]>('/policy/packs'),
  updatePack: (slug: string, enabled_globally: boolean) =>
    apiFetch<PolicyPack>(`/policy/packs/${slug}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled_globally }),
    }),
  refreshPack: (slug: string) =>
    apiFetch<{ slug: string; domain_count: number; message: string }>(
      `/policy/packs/${slug}/refresh`,
      { method: 'POST' },
    ),
  listProfiles: () => apiFetch<PolicyProfile[]>('/policy/profiles'),
  getSyncStatus: () => apiFetch<PolicySyncStatus>('/policy/sync-status'),
  applyPolicy: () =>
    apiFetch<PolicyApplyResult>('/policy/apply', {
      method: 'POST',
    }),
  getDeviceAssignment: (deviceId: number) =>
    apiFetch<DevicePolicyAssignment>(`/devices/${deviceId}/policy-assignment`),
  assignProfile: (deviceId: number, policy_profile_slug: string) =>
    apiFetch<DevicePolicyAssignment>(`/devices/${deviceId}/policy-assignment`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ policy_profile_slug }),
    }),
};
