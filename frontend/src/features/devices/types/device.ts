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

export type BehaviorReviewSource = 'template' | 'llm';

export interface BehaviorReview {
  device_id: number;
  generated_at: string;
  summary: string;
  source: BehaviorReviewSource;
  review_mode: string;
  llm_model?: string | null;
  llm_error?: string | null;
}

export interface CountryCountItem {
  country_code: string;
  country_name: string;
  query_count: number;
  share_percent: number;
  first_seen_at?: string | null;
  last_seen_at?: string | null;
  is_new?: boolean;
}

export interface DeviceCountryBreakdown {
  device_id: number;
  period_hours: number;
  total_queries: number;
  primary_country_code: string | null;
  primary_country_name: string | null;
  countries: CountryCountItem[];
  note?: string | null;
  known_regions_count?: number;
}

export interface DeviceCountrySummary {
  device_id: number;
  primary_country_code: string | null;
  primary_country_name: string | null;
}

export interface DeviceCountrySummaryList {
  items: DeviceCountrySummary[];
  period_hours: number;
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
