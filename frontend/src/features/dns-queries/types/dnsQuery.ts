export interface DnsQuery {
  id: number;
  timestamp: string;
  client_ip: string;
  device_name?: string | null;
  device_vendor?: string | null;
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
  period: {
    start: string;
    end: string;
  };
}
