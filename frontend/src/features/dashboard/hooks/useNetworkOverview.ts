import { useCallback, useEffect, useRef, useState } from 'react';
import { dashboardApi } from '../config/dashboardApi';
import { NetworkOverview } from '../types/networkOverview';

const REFRESH_MS = 60_000;

export function useNetworkOverview(periodMinutes = 60) {
  const [data, setData] = useState<NetworkOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const initialLoadDone = useRef(false);

  const refetch = useCallback(async (refresh = false) => {
    setLoading(true);
    setError(null);
    try {
      const overview = await dashboardApi.networkOverview(periodMinutes, refresh);
      setData(overview);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load AI overview';
      setError(message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [periodMinutes]);

  useEffect(() => {
    const bypassCache = !initialLoadDone.current;
    initialLoadDone.current = true;
    refetch(bypassCache);
    const id = window.setInterval(() => refetch(false), REFRESH_MS);
    return () => window.clearInterval(id);
  }, [refetch]);

  return { data, loading, error, refetch };
}
