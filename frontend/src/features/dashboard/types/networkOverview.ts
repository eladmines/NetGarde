export interface NetworkOverviewStats {
  reporting_clients: number;
  live_total_mib_per_sec: number;
  peak_mib_per_sec: number;
  alerts_total: number;
  blocked_queries: number;
  enabled_policy_packs: number;
  elevated_behavior_clients: number;
}

export interface NetworkOverview {
  generated_at: string;
  period_minutes: number;
  bullets: string[];
  stats: NetworkOverviewStats;
}
