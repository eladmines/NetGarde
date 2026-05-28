import { VpnTopologyApi } from '../types/vpnTopology';
import { TopologyEdge, TopologyNode, VpnTopologyGraph } from './types';

const NODE_W = 108;
const NODE_H = 108;
const CENTER_X = 400;
const INTERNET_Y = 8;
const SERVER_Y = 118;
const PEER_RADIUS = 165;
const PEER_Y_BASE = 300;

export const VIEWBOX_W = 800;
export const VIEWBOX_H = 440;
export const ICON_CONNECT_RADIUS = 30;

function truncateKey(key: string): string {
  if (key.length <= 12) return key;
  return `${key.slice(0, 6)}…${key.slice(-4)}`;
}

function peerLabel(peer: VpnTopologyApi['peers'][0]): string {
  return peer.hostname || peer.client_ip;
}

function statusDetail(peer: VpnTopologyApi['peers'][0]): string {
  switch (peer.handshake_status) {
    case 'connected':
      return 'Tunnel up';
    case 'idle':
      return 'No recent handshake';
    case 'never':
      return 'Not connected yet';
    default:
      return peer.on_wireguard ? 'On wg0' : 'Enrolled';
  }
}

export function buildVpnTopology(
  data: VpnTopologyApi,
  liveDnsIps: Set<string>,
): VpnTopologyGraph {
  const nodes: TopologyNode[] = [
    {
      id: 'internet',
      kind: 'internet',
      label: 'Internet',
      sublabel: 'WAN',
      x: CENTER_X - NODE_W / 2,
      y: INTERNET_Y,
      width: NODE_W,
      height: NODE_H,
    },
    {
      id: 'vpn_server',
      kind: 'vpn_server',
      label: 'WireGuard server',
      sublabel: data.server.interface,
      detail: `${data.server.gateway_ip} · ${data.server.endpoint}`,
      x: CENTER_X - NODE_W / 2,
      y: SERVER_Y,
      width: NODE_W,
      height: NODE_H,
    },
  ];

  const edges: TopologyEdge[] = [
    { id: 'wan', from: 'internet', to: 'vpn_server', label: 'UDP' },
  ];

  const peers = data.peers;
  const count = peers.length;
  const startAngle = count <= 1 ? Math.PI / 2 : Math.PI / 6;
  const endAngle = count <= 1 ? Math.PI / 2 : Math.PI - Math.PI / 6;
  const step = count <= 1 ? 0 : (endAngle - startAngle) / Math.max(count - 1, 1);

  peers.forEach((peer, index) => {
    const angle = count <= 1 ? Math.PI / 2 : startAngle + step * index;
    const cx = CENTER_X + PEER_RADIUS * Math.cos(angle);
    const cy = PEER_Y_BASE + PEER_RADIUS * 0.35 * Math.sin(angle);
    const id = `peer-${peer.peer_id}`;
    const isLiveDns = liveDnsIps.has(peer.client_ip);

    nodes.push({
      id,
      kind: 'vpn_peer',
      label: peerLabel(peer),
      sublabel: `${peer.client_ip}/32`,
      detail: `${statusDetail(peer)} · ${truncateKey(peer.public_key)}`,
      x: cx - NODE_W / 2,
      y: cy - NODE_H / 2,
      width: NODE_W,
      height: NODE_H,
      handshakeStatus: peer.handshake_status,
      isLiveDns,
      deviceId: peer.device_id ?? undefined,
      href: peer.device_id ? `/client-profiles?device=${peer.device_id}` : undefined,
    });

    edges.push({
      id: `tunnel-${peer.peer_id}`,
      from: 'vpn_server',
      to: id,
      label: peer.handshake_status === 'connected' ? 'tunnel' : undefined,
    });
  });

  return {
    nodes,
    edges,
    serverEndpoint: data.server.endpoint,
    vpnCidr: data.server.cidr,
    gatewayIp: data.server.gateway_ip,
  };
}

export function nodeCenter(node: TopologyNode): { x: number; y: number } {
  return { x: node.x + node.width / 2, y: node.y + node.height / 2 };
}

function pointToward(
  cx: number,
  cy: number,
  tx: number,
  ty: number,
  radius: number,
): { x: number; y: number } {
  const dx = tx - cx;
  const dy = ty - cy;
  const len = Math.hypot(dx, dy) || 1;
  return { x: cx + (dx / len) * radius, y: cy + (dy / len) * radius };
}

export function edgeEndpoints(
  from: TopologyNode,
  to: TopologyNode,
  radius: number = ICON_CONNECT_RADIUS,
): { x1: number; y1: number; x2: number; y2: number } {
  const a = nodeCenter(from);
  const b = nodeCenter(to);
  const p1 = pointToward(a.x, a.y, b.x, b.y, radius);
  const p2 = pointToward(b.x, b.y, a.x, a.y, radius);
  return { x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y };
}

/** Dashed subnet group behind server + peers */
export function vpnSubnetBounds(nodes: TopologyNode[]): {
  x: number;
  y: number;
  width: number;
  height: number;
} | null {
  const inSubnet = nodes.filter((n) => n.kind === 'vpn_server' || n.kind === 'vpn_peer');
  if (inSubnet.length === 0) return null;
  const pad = 24;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const n of inSubnet) {
    minX = Math.min(minX, n.x);
    minY = Math.min(minY, n.y);
    maxX = Math.max(maxX, n.x + n.width);
    maxY = Math.max(maxY, n.y + n.height);
  }
  return {
    x: minX - pad,
    y: minY - pad,
    width: maxX - minX + pad * 2,
    height: maxY - minY + pad * 2,
  };
}
