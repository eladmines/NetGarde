import { useState, useCallback, useEffect } from 'react';
import { DnsQueryStats } from '../types/dnsQuery';
import { DNS_QUERY_ENDPOINTS } from '../config/api';
import { getAdminAuthHeaders } from '../../../shared/utils/authHeaders';

export function useDnsStats() {
  const [stats, setStats] = useState<DnsQueryStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      const url = DNS_QUERY_ENDPOINTS.dnsStats();
      const response = await fetch(url, { headers: getAdminAuthHeaders() });
      if (response.ok) {
        const data: DnsQueryStats = await response.json();
        setStats(data);
      } else {
        console.error('Failed to fetch DNS stats:', response.status);
        setStats(null);
      }
    } catch (error) {
      console.error('Error fetching DNS stats:', error);
      setStats(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    refetch: fetchStats,
  };
}
