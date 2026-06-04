import { useCallback, useEffect, useState } from 'react';
import { dashboardApi } from '../config/dashboardApi';
import { NetworkOverview } from '../types/networkOverview';

const REFRESH_MS = 60_000;

export function useNetworkOverview(periodMinutes = 60) {
  const [data, setData] = useState<NetworkOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const overview = await dashboardApi.networkOverview(periodMinutes);
      setData(overview);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load network review';
      setError(message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [periodMinutes]);

  useEffect(() => {
    refetch();
    const id = window.setInterval(refetch, REFRESH_MS);
    return () => window.clearInterval(id);
  }, [refetch]);

  return { data, loading, error, refetch };
}
