export interface PolicyPack {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  enabled_globally: boolean;
  domain_count: number;
  blocked_sites_count?: number;
  domain_list_source?: 'snapshot' | 'seed' | 'empty';
}

export interface PolicyPackDomainsPage {
  slug: string;
  domains: string[];
  total: number;
  skip: number;
  limit: number;
  domain_list_source: string;
  query: string;
}

export interface ForbiddenCountryRule {
  user_country: string;
  user_country_name: string;
  blocked_countries: string[];
  blocked_country_names: string[];
}

export interface ForbiddenCountryPolicy {
  enabled: boolean;
  user_country_source: string;
  rules: ForbiddenCountryRule[];
  vpn_login_block_enabled: boolean;
  blocked_vpn_login_countries: string[];
  blocked_vpn_login_country_names: string[];
}

export interface PolicyProfile {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  enabled_pack_slugs: string[];
  extra_block_domains: string[];
  allowlist_domains: string[];
  schedule_rules: ScheduleRule[];
  behavior_sensitivity: 'low' | 'medium' | 'high';
  quarantine_on_abnormal: boolean;
  quarantine_hours: number;
  is_builtin: boolean;
}

export interface ScheduleRule {
  days: number[];
  start: string;
  end: string;
  pack_slugs: string[];
}

export interface PolicySyncStatus {
  last_sync_at: string | null;
  last_success: boolean | null;
  last_message: string | null;
}

export interface PolicyApplyResult {
  queued: boolean;
  message: string;
}

export interface DevicePolicyAssignment {
  device_id: number;
  policy_profile_id: number | null;
  policy_profile_slug: string | null;
  policy_profile_name: string | null;
  in_quarantine: boolean;
  quarantine_expires_at: string | null;
}
