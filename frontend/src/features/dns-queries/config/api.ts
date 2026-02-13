const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const DNS_QUERY_ENDPOINTS = {
  dnsQueries: (params?: {
    page?: number;
    page_size?: number;
    domain_search?: string;
    client_ip?: string;
    blocked_only?: boolean;
    start_date?: string;
    end_date?: string;
  }) => {
    const url = new URL(`${API_BASE_URL}/dns-queries`);
    if (params) {
      if (params.page !== undefined) url.searchParams.append('page', params.page.toString());
      if (params.page_size !== undefined) url.searchParams.append('page_size', params.page_size.toString());
      if (params.domain_search) url.searchParams.append('domain_search', params.domain_search.trim());
      if (params.client_ip) url.searchParams.append('client_ip', params.client_ip.trim());
      if (params.blocked_only !== undefined) url.searchParams.append('blocked_only', params.blocked_only.toString());
      if (params.start_date) url.searchParams.append('start_date', params.start_date);
      if (params.end_date) url.searchParams.append('end_date', params.end_date);
    }
    return url.toString();
  },
  dnsStats: (params?: { start_date?: string; end_date?: string }) => {
    const url = new URL(`${API_BASE_URL}/dns-queries/stats`);
    if (params) {
      if (params.start_date) url.searchParams.append('start_date', params.start_date);
      if (params.end_date) url.searchParams.append('end_date', params.end_date);
    }
    return url.toString();
  },
  dnsClients: () => `${API_BASE_URL}/dns-queries/clients`,
  dnsSites: (params?: {
    start_date?: string;
    end_date?: string;
    client_ip?: string;
    blocked_only?: boolean;
    filter_noise?: boolean;
    limit?: number;
  }) => {
    const url = new URL(`${API_BASE_URL}/dns-queries/sites`);
    if (params) {
      if (params.start_date) url.searchParams.append('start_date', params.start_date);
      if (params.end_date) url.searchParams.append('end_date', params.end_date);
      if (params.client_ip) url.searchParams.append('client_ip', params.client_ip.trim());
      if (params.blocked_only !== undefined) url.searchParams.append('blocked_only', params.blocked_only.toString());
      if (params.filter_noise !== undefined) url.searchParams.append('filter_noise', params.filter_noise.toString());
      if (params.limit !== undefined) url.searchParams.append('limit', params.limit.toString());
    }
    return url.toString();
  },
};
