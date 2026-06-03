import { useCallback, useEffect, useState } from 'react';
import { devicesApi } from '../../devices/config/api';
import { Device } from '../../devices/types/device';
import {
  isClientActiveNow,
  subscribeDnsClientActivity,
} from '../../dns-queries/dnsClientActivity';
import { ClientBandwidth } from '../types/usageLive';

export interface LiveClientRow {
  client_ip: string;
  hostname: string | null;
  mac_address: string | null;
  source: string | null;
  device_id: number | null;
  /** DNS activity in the last few minutes (WebSocket feed). */
  is_active_now: boolean;
  /** Latest VPN tunnel throughput from /devices/usage/live. */
  bandwidth: ClientBandwidth | null;
}

const POLL_MS = 12_000;
const USAGE_POLL_MS = 4_000;

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

function buildRows(devices: Device[]): LiveClientRow[] {
  return devices.map((device) => ({
    client_ip: device.client_ip,
    hostname: device.hostname,
    mac_address: device.mac_address,
    source: device.source,
    device_id: device.id,
    is_active_now: false,
    bandwidth: null,
  }));
}

function buildUsageMaps(
  items: Awaited<ReturnType<typeof devicesApi.listUsageLive>>['items'],
): {
  byDeviceId: Map<number, ClientBandwidth>;
  byClientIp: Map<string, ClientBandwidth>;
} {
  const byDeviceId = new Map<number, ClientBandwidth>();
  const byClientIp = new Map<string, ClientBandwidth>();
  const toBw = (item: (typeof items)[number]): ClientBandwidth => ({
    rx_mib_per_sec: item.rx_mib_per_sec,
    tx_mib_per_sec: item.tx_mib_per_sec,
    total_mib_per_sec: item.total_mib_per_sec,
    delta_rx_bytes: item.delta_rx_bytes,
    delta_tx_bytes: item.delta_tx_bytes,
    recorded_at: item.recorded_at,
  });
  for (const item of items) {
    const bw = toBw(item);
    if (item.device_id != null) {
      byDeviceId.set(item.device_id, bw);
    }
    if (item.client_ip) {
      byClientIp.set(item.client_ip, bw);
    }
  }
  return { byDeviceId, byClientIp };
}

function attachBandwidth(
  rows: LiveClientRow[],
  byDeviceId: Map<number, ClientBandwidth>,
  byClientIp: Map<string, ClientBandwidth>,
): LiveClientRow[] {
  return rows.map((row) => {
    const bw =
      (row.device_id != null ? byDeviceId.get(row.device_id) : undefined) ??
      byClientIp.get(row.client_ip);
    return bw ? { ...row, bandwidth: bw } : row;
  });
}

/** Registered devices with DNS activity in the live feed window. */
function filterLiveRegisteredClients(rows: LiveClientRow[]): LiveClientRow[] {
  return rows.filter((row) => row.device_id != null && row.is_active_now);
}

function sortClients(rows: LiveClientRow[]): LiveClientRow[] {
  return [...rows].sort((a, b) => {
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
  const [usageByDevice, setUsageByDevice] = useState<Map<number, ClientBandwidth>>(new Map());
  const [usageByIp, setUsageByIp] = useState<Map<string, ClientBandwidth>>(new Map());
  const [clients, setClients] = useState<LiveClientRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usageError, setUsageError] = useState<string | null>(null);

  const recomputeClients = useCallback(() => {
    const base = sortClients(
      filterLiveRegisteredClients(withLiveActivity(buildRows(devices))),
    );
    setClients(attachBandwidth(base, usageByDevice, usageByIp));
  }, [devices, usageByDevice, usageByIp]);

  useEffect(() => {
    recomputeClients();
  }, [recomputeClients]);

  useEffect(() => subscribeDnsClientActivity(recomputeClients), [recomputeClients]);

  const fetchAll = useCallback(async () => {
    setError(null);
    try {
      const deviceList = await devicesApi.list();
      setDevices(deviceList);
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

  const fetchUsage = useCallback(async () => {
    try {
      const resp = await devicesApi.listUsageLive();
      const maps = buildUsageMaps(resp.items);
      setUsageByDevice(maps.byDeviceId);
      setUsageByIp(maps.byClientIp);
      setUsageError(null);
    } catch (e) {
      setUsageError(e instanceof Error ? e.message : 'Failed to load bandwidth');
    }
  }, []);

  useEffect(() => {
    fetchUsage();
    const id = setInterval(fetchUsage, USAGE_POLL_MS);
    return () => clearInterval(id);
  }, [fetchUsage]);

  const enrolledCount = clients.filter((c) => c.source === 'vpn_enroll').length;

  const aggregateBandwidth = clients.reduce(
    (acc, c) => {
      if (!c.bandwidth) {
        return acc;
      }
      return {
        rx_mib_per_sec: acc.rx_mib_per_sec + c.bandwidth.rx_mib_per_sec,
        tx_mib_per_sec: acc.tx_mib_per_sec + c.bandwidth.tx_mib_per_sec,
        total_mib_per_sec: acc.total_mib_per_sec + c.bandwidth.total_mib_per_sec,
      };
    },
    { rx_mib_per_sec: 0, tx_mib_per_sec: 0, total_mib_per_sec: 0 },
  );

  const refetch = useCallback(async () => {
    await Promise.all([fetchAll(), fetchUsage()]);
  }, [fetchAll, fetchUsage]);

  return {
    clients,
    loading,
    error,
    usageError,
    enrolledCount,
    aggregateBandwidth,
    refetch,
  };
}
