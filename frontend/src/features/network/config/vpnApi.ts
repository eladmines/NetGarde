import { API_BASE_URL } from '../../../shared/config/apiBaseUrl';
import { getAdminAuthHeaders } from '../../../shared/utils/authHeaders';
import { VpnTopologyApi } from '../types/vpnTopology';

export async function fetchVpnTopology(): Promise<VpnTopologyApi> {
  const res = await fetch(`${API_BASE_URL}/vpn/topology`, {
    headers: {
      Accept: 'application/json',
      ...getAdminAuthHeaders(),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<VpnTopologyApi>;
}
