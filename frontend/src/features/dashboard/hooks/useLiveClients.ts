import { useCallback, useEffect, useState } from 'react';
import { devicesApi } from '../../devices/config/api';
import { Device } from '../../devices/types/device';
import { DNS_QUERY_ENDPOINTS } from '../../dns-queries/config/api';
import { DnsQueryStats } from '../../dns-queries/types/dnsQuery';
import { getAdminAuthHeaders } from '../../../shared/utils/authHeaders';
import {
  isClientActiveNow,
  subscribeDnsClientActivity,
} from '../../dns-queries/dnsClientActivity';

export interface LiveClientRow {
  client_ip: string;
  hostname: string | null;
  mac_address: string | null;
  source: string | null;
  device_id: number | null;
  query_count: number;
  /** Seen on the live DNS ingest path (since server start when stats are live). */
  has_dns_traffic: boolean;
  /** DNS activity in the last few minutes (WebSocket feed). */
  is_active_now: boolean;
}

const POLL_MS = 12_000;

function sourceLabel(source: string | null): string {
  switch (source) {
    case 'vpn_enroll':
      return 'VPN enrolled';
    case 'dhcp_lease':
      return 'DHCP';
    case 'dns_observed':
      return 'DNS observed';
    case 'manual':
      return 'Manual';
    default:
      return source || 'Unknown';
  }
}

export function formatClientSource(source: string | null): string {
  return sourceLabel(source);
}

function buildRows(
  devices: Device[],
  clientIps: Set<string>,
  queryCounts: Map<string, number>,
): LiveClientRow[] {
  const byIp = new Map<string, LiveClientRow>();

  for (const device of devices) {
    const count = queryCounts.get(device.client_ip) ?? 0;
    byIp.set(device.client_ip, {
      client_ip: device.client_ip,
      hostname: device.hostname,
      mac_address: device.mac_address,
      source: device.source,
      device_id: device.id,
      query_count: count,
      has_dns_traffic: clientIps.has(device.client_ip),
      is_active_now: false,
    });
  }

  return Array.from(byIp.values());
}

/** Registered devices with DNS activity in the live feed window. */
function filterLiveRegisteredClients(rows: LiveClientRow[]): LiveClientRow[] {
  return rows.filter((row) => row.device_id != null && row.is_active_now);
}

function sortClients(rows: LiveClientRow[]): LiveClientRow[] {
  return [...rows].sort((a, b) => {
    if (b.query_count !== a.query_count) return b.query_count - a.query_count;
    const nameA = (a.hostname || a.client_ip).toLowerCase();
    const nameB = (b.hostname || b.client_ip).toLowerCase();
    return nameA.localeCompare(nameB);
  });
}

function withLiveActivity(rows: LiveClientRow[]): LiveClientRow[] {
  return rows.map((row) => ({
    ...row,
    is_active_now: isClientActiveNow(row.client_ip),
  }));
}

export function useLiveClients() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [clientIps, setClientIps] = useState<Set<string>>(new Set());
  const [queryCounts, setQueryCounts] = useState<Map<string, number>>(new Map());
  const [statsSource, setStatsSource] = useState<string | null>(null);
  const [clients, setClients] = useState<LiveClientRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const recomputeClients = useCallback(() => {
    setClients(
      sortClients(
        filterLiveRegisteredClients(withLiveActivity(buildRows(devices, clientIps, queryCounts))),
      ),
    );
  }, [devices, clientIps, queryCounts]);

  useEffect(() => {
    recomputeClients();
  }, [recomputeClients]);

  useEffect(() => subscribeDnsClientActivity(recomputeClients), [recomputeClients]);

  const fetchAll = useCallback(async () => {
    setError(null);
    try {
      const headers = getAdminAuthHeaders();
      const [deviceList, clientsRes, statsRes] = await Promise.all([
        devicesApi.list(),
        fetch(DNS_QUERY_ENDPOINTS.dnsClients(), { headers }),
        fetch(DNS_QUERY_ENDPOINTS.dnsStats(), { headers }),
      ]);

      setDevices(deviceList);

      if (clientsRes.ok) {
        const ips: string[] = await clientsRes.json();
        setClientIps(new Set(ips));
      } else {
        setClientIps(new Set());
      }

      if (statsRes.ok) {
        const stats: DnsQueryStats = await statsRes.json();
        setStatsSource(stats.source ?? null);
        const counts = new Map<string, number>();
        for (const item of stats.top_clients) {
          counts.set(item.client_ip, item.count);
        }
        setQueryCounts(counts);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load clients');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, POLL_MS);
    return () => clearInterval(id);
  }, [fetchAll]);

  const enrolledCount = clients.filter((c) => c.source === 'vpn_enroll').length;

  return {
    clients,
    loading,
    error,
    statsSource,
    enrolledCount,
    refetch: fetchAll,
  };
}
