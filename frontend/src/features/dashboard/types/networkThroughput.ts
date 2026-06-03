export interface ServerNetworkThroughput {
  rx_mib_per_sec: number;
  tx_mib_per_sec: number;
  total_mib_per_sec: number;
  reporting_clients: number;
}

export interface NetworkThroughputPoint extends ServerNetworkThroughput {
  ts: number;
  label: string;
}
