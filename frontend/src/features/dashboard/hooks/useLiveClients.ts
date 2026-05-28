import { useCallback, useEffect, useState } from 'react';
import { devicesApi } from '../../devices/config/api';
import { Device } from '../../devices/types/device';
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

function buildRows(devices: Device[]): LiveClientRow[] {
  return devices.map((device) => ({
    client_ip: device.client_ip,
    hostname: device.hostname,
    mac_address: device.mac_address,
    source: device.source,
    device_id: device.id,
    is_active_now: false,
  }));
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
  const [clients, setClients] = useState<LiveClientRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const recomputeClients = useCallback(() => {
    setClients(
      sortClients(filterLiveRegisteredClients(withLiveActivity(buildRows(devices)))),
    );
  }, [devices]);

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

  const enrolledCount = clients.filter((c) => c.source === 'vpn_enroll').length;

  return {
    clients,
    loading,
    error,
    enrolledCount,
    refetch: fetchAll,
  };
}
