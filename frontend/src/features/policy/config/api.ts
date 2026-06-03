import { getAdminAuthHeaders } from '../../../shared/utils/authHeaders';
import { API_BASE_URL } from '../../../shared/config/apiBaseUrl';
import {
  DevicePolicyAssignment,
  PolicyApplyResult,
  PolicyPack,
  PolicyPackDomainsPage,
  PolicyProfile,
  PolicySyncStatus,
} from '../types/policy';

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
  listPackDomains: (
    slug: string,
    params: { q?: string; skip?: number; limit?: number } = {},
  ) => {
    const sp = new URLSearchParams();
    if (params.q) {
      sp.set('q', params.q);
    }
    if (params.skip != null) {
      sp.set('skip', String(params.skip));
    }
    if (params.limit != null) {
      sp.set('limit', String(params.limit));
    }
    const qs = sp.toString();
    return apiFetch<PolicyPackDomainsPage>(
      `/policy/packs/${slug}/domains${qs ? `?${qs}` : ''}`,
    );
  },
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
