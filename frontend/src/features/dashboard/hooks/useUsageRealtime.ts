import { useCallback, useEffect, useRef, useState } from 'react';
import { devicesApi } from '../../devices/config/api';
import { getUsageWebSocketUrl } from '../../../shared/config/apiWebSocketUrl';
import {
  UsageHistoryPoint,
  UsageWsSnapshot,
  UsageWsUpdate,
} from '../types/usageHistory';
import { DeviceUsageLiveItem } from '../types/usageLive';
import {
  NetworkThroughputPoint,
  ServerNetworkThroughput,
} from '../types/networkThroughput';
import { pruneThroughputHistory } from '../utils/throughputHistory';
import { aggregateServerUsage } from '../utils/usageAggregate';

const RECONNECT_DELAY = 3000;
const PING_INTERVAL = 25000;
const FALLBACK_POLL_MS = 30_000;

function historyPointToChart(p: UsageHistoryPoint): NetworkThroughputPoint {
  return {
    rx_mib_per_sec: p.rx_mib_per_sec,
    tx_mib_per_sec: p.tx_mib_per_sec,
    total_mib_per_sec: p.total_mib_per_sec,
    reporting_clients: p.reporting_clients,
    ts: new Date(p.recorded_at).getTime(),
    label: '',
  };
}

function appendHistoryPoint(
  prev: NetworkThroughputPoint[],
  point: UsageHistoryPoint,
): NetworkThroughputPoint[] {
  const now = Date.now();
  const chartPoint = historyPointToChart(point);
  const last = prev[prev.length - 1];
  if (last && last.ts === chartPoint.ts) {
    return pruneThroughputHistory([...prev.slice(0, -1), chartPoint], now);
  }
  return pruneThroughputHistory([...prev, chartPoint], now);
}

function historyToChart(points: UsageHistoryPoint[]): NetworkThroughputPoint[] {
  const now = Date.now();
  return pruneThroughputHistory(points.map(historyPointToChart), now);
}

export interface UseUsageRealtimeResult {
  liveItems: DeviceUsageLiveItem[];
  serverThroughput: ServerNetworkThroughput;
  throughputHistory: NetworkThroughputPoint[];
  usageError: string | null;
  isConnected: boolean;
  refetchUsage: () => Promise<void>;
}

export function useUsageRealtime(): UseUsageRealtimeResult {
  const [liveItems, setLiveItems] = useState<DeviceUsageLiveItem[]>([]);
  const [serverThroughput, setServerThroughput] = useState<ServerNetworkThroughput>({
    rx_mib_per_sec: 0,
    tx_mib_per_sec: 0,
    total_mib_per_sec: 0,
    reporting_clients: 0,
  });
  const [throughputHistory, setThroughputHistory] = useState<NetworkThroughputPoint[]>([]);
  const [usageError, setUsageError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const applyLiveItems = useCallback((items: DeviceUsageLiveItem[]) => {
    setLiveItems(items);
    setServerThroughput(aggregateServerUsage(items));
  }, []);

  const loadFromRest = useCallback(async () => {
    try {
      const [historyResp, liveResp] = await Promise.all([
        devicesApi.listUsageHistory(60),
        devicesApi.listUsageLive(),
      ]);
      setThroughputHistory(historyToChart(historyResp.points));
      applyLiveItems(liveResp.items);
      setUsageError(null);
    } catch (e) {
      setUsageError(e instanceof Error ? e.message : 'Failed to load bandwidth');
    }
  }, [applyLiveItems]);

  const refetchUsage = loadFromRest;

  const stopPing = useCallback(() => {
    if (pingTimerRef.current) {
      clearInterval(pingTimerRef.current);
      pingTimerRef.current = null;
    }
  }, []);

  const startPing = useCallback(() => {
    stopPing();
    pingTimerRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, PING_INTERVAL);
  }, [stopPing]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = getUsageWebSocketUrl();
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        startPing();
      };

      ws.onmessage = (event) => {
        const raw = event.data;
        if (raw === 'pong') {
          return;
        }
        try {
          const data = JSON.parse(raw) as UsageWsSnapshot | UsageWsUpdate;
          if (data.type === 'usage_snapshot') {
            const snap = data as UsageWsSnapshot;
            setThroughputHistory(historyToChart(snap.history.points));
            applyLiveItems(snap.live.items);
            setUsageError(null);
          } else if (data.type === 'usage_update') {
            const upd = data as UsageWsUpdate;
            setThroughputHistory((prev) => appendHistoryPoint(prev, upd.aggregate_point));
            applyLiveItems(upd.live.items);
            setUsageError(null);
          }
        } catch (e) {
          console.warn('[UsageRealtime] Failed to parse WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        stopPing();
        if (reconnectTimerRef.current) {
          clearTimeout(reconnectTimerRef.current);
        }
        reconnectTimerRef.current = setTimeout(connect, RECONNECT_DELAY);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch (e) {
      console.warn('[UsageRealtime] WebSocket connect failed:', e);
      setIsConnected(false);
    }
  }, [applyLiveItems, startPing, stopPing]);

  useEffect(() => {
    loadFromRest();
    connect();
    return () => {
      stopPing();
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [connect, loadFromRest, stopPing]);

  useEffect(() => {
    if (isConnected) {
      return;
    }
    const id = setInterval(loadFromRest, FALLBACK_POLL_MS);
    return () => clearInterval(id);
  }, [isConnected, loadFromRest]);

  return {
    liveItems,
    serverThroughput,
    throughputHistory,
    usageError,
    isConnected,
    refetchUsage,
  };
}
