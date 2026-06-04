import { useEffect, useMemo, useState } from 'react';
import { devicesApi } from '../config/api';
import { DeviceLoginGeoSummary } from '../types/device';

export function useDeviceLoginGeoSummaries() {
  const [items, setItems] = useState<DeviceLoginGeoSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    devicesApi
      .listLoginLocationSummaries()
      .then((res) => {
        if (!cancelled) setItems(res.items);
      })
      .catch(() => {
        if (!cancelled) setItems([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const byDeviceId = useMemo(() => {
    const map = new Map<number, DeviceLoginGeoSummary>();
    for (const item of items) {
      map.set(item.device_id, item);
    }
    return map;
  }, [items]);

  return { items, byDeviceId, loading };
}
