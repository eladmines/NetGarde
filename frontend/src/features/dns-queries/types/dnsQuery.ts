export interface DnsQuery {
  id: number;
  timestamp: string;
  client_ip: string;
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
