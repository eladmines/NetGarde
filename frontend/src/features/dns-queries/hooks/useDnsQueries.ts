import { useState, useCallback, useEffect } from 'react';
import { getAdminAuthHeaders } from '../../../shared/utils/authHeaders';
import { DnsQuery, DnsQueryPaginatedResponse } from '../types/dnsQuery';
import { DNS_QUERY_ENDPOINTS } from '../config/api';

export function useDnsQueries() {
  const [queries, setQueries] = useState<DnsQuery[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [domainSearch, setDomainSearch] = useState('');
  const [clientIp, setClientIp] = useState('');
  const [blockedOnly, setBlockedOnly] = useState(false);

  const fetchQueries = useCallback(async () => {
    try {
      setLoading(true);
      const url = DNS_QUERY_ENDPOINTS.dnsQueries({
        page,
        page_size: pageSize,
        domain_search: domainSearch || undefined,
        client_ip: clientIp || undefined,
        blocked_only: blockedOnly || undefined,
      });

      const response = await fetch(url, { headers: getAdminAuthHeaders() });
      if (response.ok) {
        const data: DnsQueryPaginatedResponse = await response.json();
        setQueries(data.items);
        setTotalCount(data.total);
      } else {
        console.error('Failed to fetch DNS queries:', response.status);
        setQueries([]);
        setTotalCount(0);
      }
    } catch (error) {
      console.error('Error fetching DNS queries:', error);
      setQueries([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, domainSearch, clientIp, blockedOnly]);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [domainSearch, clientIp, blockedOnly]);

  useEffect(() => {
    fetchQueries();
  }, [fetchQueries]);

  return {
    queries,
    loading,
    totalCount,
    page,
    pageSize,
    setPage,
    setPageSize,
    domainSearch,
    setDomainSearch,
    clientIp,
    setClientIp,
    blockedOnly,
    setBlockedOnly,
    refetch: fetchQueries,
  };
}
