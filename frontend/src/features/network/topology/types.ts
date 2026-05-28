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

export interface TopologyLayoutMetrics {
  clientX: number;
  busX: number;
  serverX: number;
  internetX: number;
  busY1: number;
  busY2: number;
  midY: number;
}

export interface VpnTopologyGraph {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  serverEndpoint: string;
  vpnCidr: string;
  gatewayIp: string;
  viewWidth: number;
  viewHeight: number;
  layout: TopologyLayoutMetrics;
}
