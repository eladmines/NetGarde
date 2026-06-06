export interface ServerNetworkThroughput {
  rx_mib_per_sec: number;
  tx_mib_per_sec: number;
  total_mib_per_sec: number;
  reporting_clients: number;
}

export interface NetworkThroughputPoint extends ServerNetworkThroughput {
  /** Unix ms — used for time axis and 60-minute window. */
  ts: number;
  /** Legacy display label; chart uses `ts` with automatic formatting. */
  label: string;
}
