import { useCallback, useEffect, useState } from 'react';
import { devicesApi } from '../config/api';
import { DeviceCountrySummary } from '../types/device';

export function useDeviceCountrySummaries(periodHours = 168) {
  const [byDeviceId, setByDeviceId] = useState<Map<number, DeviceCountrySummary>>(new Map());
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const res = await devicesApi.listCountrySummaries(periodHours);
      const map = new Map<number, DeviceCountrySummary>();
      for (const item of res.items) {
        map.set(item.device_id, item);
      }
      setByDeviceId(map);
    } catch {
      setByDeviceId(new Map());
    } finally {
      setLoading(false);
    }
  }, [periodHours]);

  useEffect(() => {
    load();
    const id = setInterval(load, 60_000);
    return () => clearInterval(id);
  }, [load]);

  return { byDeviceId, loading, refresh: load };
}
