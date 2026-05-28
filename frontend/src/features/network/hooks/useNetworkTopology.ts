import { useCallback, useEffect, useState } from 'react';
import { isClientActiveNow, subscribeDnsClientActivity } from '../../dns-queries/dnsClientActivity';
import { fetchVpnTopology } from '../config/vpnApi';
import { buildVpnTopology } from '../topology/buildVpnTopology';
import { VpnTopologyGraph } from '../topology/types';
import { VpnTopologyApi } from '../types/vpnTopology';

export function useNetworkTopology() {
  const [apiData, setApiData] = useState<VpnTopologyApi | null>(null);
  const [topology, setTopology] = useState<VpnTopologyGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activityTick, setActivityTick] = useState(0);

  useEffect(() => subscribeDnsClientActivity(() => setActivityTick((n) => n + 1)), []);

  useEffect(() => {
    if (!apiData) return;
    const liveIps = new Set(
      apiData.peers.filter((p) => isClientActiveNow(p.client_ip)).map((p) => p.client_ip),
    );
    setTopology(buildVpnTopology(apiData, liveIps));
  }, [apiData, activityTick]);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const data = await fetchVpnTopology();
      setApiData(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load VPN topology');
      setApiData(null);
      setTopology(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 15_000);
    return () => clearInterval(id);
  }, [refresh]);

  const connectedCount =
    apiData?.peers.filter((p) => p.handshake_status === 'connected').length ?? 0;
  const peerCount = apiData?.peers.length ?? 0;
  const liveDnsCount = topology?.nodes.filter((n) => n.kind === 'vpn_peer' && n.isLiveDns).length ?? 0;

  return { topology, loading, error, connectedCount, peerCount, liveDnsCount, refresh };
}
