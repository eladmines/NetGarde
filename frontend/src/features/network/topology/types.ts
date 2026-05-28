export type TopologyNodeKind =
  | 'internet'
  | 'gateway'
  | 'dns'
  | 'api'
  | 'database'
  | 'log_ingest'
  | 'client';

export interface TopologyNode {
  id: string;
  kind: TopologyNodeKind;
  label: string;
  sublabel?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  isLive?: boolean;
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

export interface NetworkTopology {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  vpnCidr: string;
  gatewayIp: string;
}
