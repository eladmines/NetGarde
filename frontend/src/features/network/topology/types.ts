export type VpnHandshakeStatus = 'connected' | 'idle' | 'never' | 'unknown';

export type TopologyNodeKind = 'internet' | 'vpn_server' | 'vpn_peer';

export interface TopologyNode {
  id: string;
  kind: TopologyNodeKind;
  label: string;
  sublabel?: string;
  detail?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  handshakeStatus?: VpnHandshakeStatus;
  isLiveDns?: boolean;
  deviceId?: number;
  href?: string;
}

export interface TopologyEdge {
  id: string;
  from: string;
  to: string;
  label?: string;
  dashed?: boolean;
}

export interface VpnTopologyGraph {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  serverEndpoint: string;
  vpnCidr: string;
  gatewayIp: string;
}
