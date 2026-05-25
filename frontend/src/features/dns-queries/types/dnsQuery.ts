export interface DnsQuery {
  id: number;
  timestamp: string;
  client_ip: string;
  device_name?: string | null;
  device_vendor?: string | null;
  user_name?: string | null;
  domain: string;
  query_type: string | null;
  action: string | null;
  blocked: boolean;
  created_at: string | null;
}

export interface DnsQueryStats {
  total_queries: number;
  blocked_queries: number;
  allowed_queries: number;
  block_rate: number;
  top_blocked_domains: { domain: string; count: number }[];
  top_clients: { client_ip: string; count: number }[];
  source?: 'live' | 'database';
  period?: {
    start: string;
    end: string;
  };
}

export interface DnsQueryPaginatedResponse {
  items: DnsQuery[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface DnsSiteGroup {
  root_domain: string;
  total_queries: number;
  subdomains: string[];
  last_seen: string | null;
  first_seen: string | null;
  blocked: boolean;
}

export interface DnsSitesResponse {
  sites: DnsSiteGroup[];
  total_sites: number;
  noise_filtered: number;
  source?: 'live' | 'database';
  period: {
    start: string;
    end: string;
  };
}

export interface DnsAlert {
  id: number;
  timestamp: string;
  client_ip: string;
  alert_type: string;
  severity: string;
  domain: string | null;
  root_domain: string | null;
  message: string | null;
  created_at: string | null;
}

export interface DnsAlertListResponse {
  items: DnsAlert[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
