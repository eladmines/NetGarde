import { useCallback, useEffect, useState } from 'react';
import { DNS_QUERY_ENDPOINTS } from '../config/api';
import { DnsAlert, DnsAlertListResponse } from '../types/dnsQuery';

export function useDnsAlerts(pageSize = 20) {
  const [items, setItems] = useState<DnsAlert[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const url = DNS_QUERY_ENDPOINTS.dnsAlerts({ page: 1, page_size: pageSize });
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data: DnsAlertListResponse = await response.json();
      setItems(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to fetch DNS alerts:', error);
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  return { items, total, loading, refetch: fetchAlerts };
}
