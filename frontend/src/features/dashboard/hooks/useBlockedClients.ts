import { useCallback, useEffect, useState } from 'react';
import { devicesApi } from '../../devices/config/api';
import { BlockedClientSummary } from '../../devices/types/device';

const POLL_MS = 15_000;

export function useBlockedClients() {
  const [clients, setClients] = useState<BlockedClientSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setError(null);
      const data = await devicesApi.listBlockedClients();
      setClients(data.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load blocked clients');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = window.setInterval(refresh, POLL_MS);
    return () => window.clearInterval(id);
  }, [refresh]);

  return { clients, loading, error, refresh };
}
