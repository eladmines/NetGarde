export interface PolicyPack {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  enabled_globally: boolean;
  domain_count: number;
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

export interface DevicePolicyAssignment {
  device_id: number;
  policy_profile_id: number | null;
  policy_profile_slug: string | null;
  policy_profile_name: string | null;
  in_quarantine: boolean;
  quarantine_expires_at: string | null;
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
