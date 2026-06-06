export interface DeviceUsageLiveItem {
  device_id: number | null;
  vpn_device_id: string;
  client_ip: string | null;
  recorded_at: string;
  interval_sec: number;
  rx_bytes: number;
  tx_bytes: number;
  delta_rx_bytes: number;
  delta_tx_bytes: number;
  rx_mib_per_sec: number;
  tx_mib_per_sec: number;
  total_mib_per_sec: number;
}

export interface DeviceUsageLiveResponse {
  items: DeviceUsageLiveItem[];
  max_age_sec: number;
}

export interface ClientBandwidth {
  rx_mib_per_sec: number;
  tx_mib_per_sec: number;
  total_mib_per_sec: number;
  delta_rx_bytes: number;
  delta_tx_bytes: number;
  recorded_at: string;
}
