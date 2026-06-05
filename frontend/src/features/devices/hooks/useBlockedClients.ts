import { useCallback, useEffect, useState } from 'react';
import { devicesApi } from '../config/api';
import { BlockedClientSummary } from '../types/device';

export function useBlockedClients() {
  const [items, setItems] = useState<BlockedClientSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await devicesApi.listBlockedClients();
      setItems(data.items);
      setTotal(data.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load blocked clients');
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { items, total, loading, error, refresh };
}
