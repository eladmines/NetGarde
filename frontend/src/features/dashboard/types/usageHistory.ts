import { DeviceUsageLiveResponse } from './usageLive';

export interface UsageHistoryPoint {
  recorded_at: string;
  rx_mib_per_sec: number;
  tx_mib_per_sec: number;
  total_mib_per_sec: number;
  reporting_clients: number;
}

export interface UsageHistoryResponse {
  points: UsageHistoryPoint[];
  minutes: number;
}

export interface UsageWsSnapshot {
  type: 'usage_snapshot';
  history: UsageHistoryResponse;
  live: DeviceUsageLiveResponse;
}

export interface UsageWsUpdate {
  type: 'usage_update';
  aggregate_point: UsageHistoryPoint;
  live: DeviceUsageLiveResponse;
}
