export type VpnHandshakeStatus = 'connected' | 'idle' | 'never' | 'unknown';

export interface VpnServerApi {
  interface: string;
  endpoint: string;
  gateway_ip: string;
  dns_ip: string;
  cidr: string;
  server_public_key: string;
  allowed_ips: string[];
  mtu?: number | null;
}

export interface VpnPeerApi {
  peer_id: number;
  vpn_device_id: string;
  device_id: number | null;
  hostname: string | null;
  client_ip: string;
  public_key: string;
  handshake_status: VpnHandshakeStatus;
  latest_handshake_at: string | null;
  endpoint: string | null;
  rx_bytes: number | null;
  tx_bytes: number | null;
  on_wireguard: boolean;
}

export interface VpnTopologyApi {
  server: VpnServerApi;
  peers: VpnPeerApi[];
}
