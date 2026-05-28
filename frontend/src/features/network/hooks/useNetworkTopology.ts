import { useCallback, useEffect, useState } from 'react';
import { devicesApi } from '../../devices/config/api';
import { Device } from '../../devices/types/device';
import { isClientActiveNow, subscribeDnsClientActivity } from '../../dns-queries/dnsClientActivity';
import { buildNetworkTopology } from '../topology/buildNetworkTopology';
import { NetworkTopology } from '../topology/types';

export function useNetworkTopology() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [topology, setTopology] = useState<NetworkTopology | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activityTick, setActivityTick] = useState(0);

  useEffect(() => subscribeDnsClientActivity(() => setActivityTick((n) => n + 1)), []);

  useEffect(() => {
    const liveIps = new Set(
      devices.filter((d) => isClientActiveNow(d.client_ip)).map((d) => d.client_ip),
    );
    setTopology(buildNetworkTopology(devices, liveIps));
  }, [devices, activityTick]);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const list = await devicesApi.list();
      setDevices(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load network');
      setDevices([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 15_000);
    return () => clearInterval(id);
  }, [refresh]);

  const liveCount = topology?.nodes.filter((n) => n.kind === 'client' && n.isLive).length ?? 0;
  const clientCount = topology?.nodes.filter((n) => n.kind === 'client').length ?? 0;

  return { topology, loading, error, liveCount, clientCount, refresh };
}
