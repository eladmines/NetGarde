import { VpnTopologyApi } from '../types/vpnTopology';
import { TopologyEdge, TopologyNode, VpnTopologyGraph } from './types';

const SERVER_W = 150;
const SERVER_H = 58;
const PEER_W = 120;
const PEER_H = 50;
const CENTER_X = 400;
const SERVER_Y = 175;
const PEER_RADIUS = 155;
const PEER_Y_BASE = 310;

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
      sublabel: 'Client networks',
      x: CENTER_X - 70,
      y: 28,
      width: 140,
      height: 44,
    },
    {
      id: 'vpn_server',
      kind: 'vpn_server',
      label: 'WireGuard server',
      sublabel: data.server.interface,
      detail: `${data.server.gateway_ip} · ${data.server.endpoint}`,
      x: CENTER_X - SERVER_W / 2,
      y: SERVER_Y,
      width: SERVER_W,
      height: SERVER_H,
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
      x: cx - PEER_W / 2,
      y: cy - PEER_H / 2,
      width: PEER_W,
      height: PEER_H,
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

export function edgeEndpoints(
  from: TopologyNode,
  to: TopologyNode,
): { x1: number; y1: number; x2: number; y2: number } {
  const a = nodeCenter(from);
  const b = nodeCenter(to);
  const dy = b.y - a.y;
  const y1 = from.y + (dy > 0 ? from.height : 0);
  const y2 = to.y + (dy > 0 ? 0 : to.height);
  return { x1: a.x, y1, x2: b.x, y2 };
}
