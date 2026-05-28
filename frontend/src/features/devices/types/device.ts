export interface Device {
  id: number;
  ip_lease_id: number;
  client_ip: string;
  hostname: string | null;
  mac_address: string | null;
  source: string;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface BehaviorProfile {
  device_id: number;
  profile_ready: boolean;
  last_score: number | null;
  last_scored_at: string | null;
  baseline: Record<string, unknown>;
  updated_at?: string | null;
}

export interface DeviceSecurityPolicy {
  device_id: number;
  auto_block_enabled: boolean;
  auto_block_threshold: number;
  max_blocks_per_day: number;
}

export interface BlockedClientSummary {
  device_id: number;
  client_ip: string | null;
  hostname: string | null;
  mac_address: string | null;
  last_score: number | null;
  last_scored_at: string | null;
  active_block_count: number;
  latest_blocked_domain: string | null;
  latest_block_at: string | null;
}

export interface BlockedClientsListResponse {
  items: BlockedClientSummary[];
  total: number;
}

export interface ClientBlockedDomain {
  id: number;
  device_id: number;
  domain: string;
  root_domain: string | null;
  source: string;
  score: number | null;
  expires_at: string | null;
  revoked_at: string | null;
  created_at?: string | null;
}
