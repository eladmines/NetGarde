import { VpnTopologyApi } from '../types/vpnTopology';
import { TopologyEdge, TopologyNode, VpnTopologyGraph } from './types';

export const DOT_R_PEER = 9;
export const DOT_R_SERVER = 14;
export const DOT_R_INTERNET = 11;

const CLIENT_X = 56;
const BUS_X = 340;
const SERVER_X = 520;
const INTERNET_X = 680;
const ROW_GAP = 64;
const TOP_PAD = 72;
const BOTTOM_PAD = 48;
const NODE_W = 200;
const NODE_H = 40;

function peerLabel(peer: VpnTopologyApi['peers'][0]): string {
  return peer.hostname || peer.client_ip;
}

export function buildVpnTopology(
  data: VpnTopologyApi,
  liveDnsIps: Set<string>,
): VpnTopologyGraph {
  const peers = data.peers;
  const peerCount = peers.length;
  const contentHeight =
    peerCount > 0 ? TOP_PAD + (peerCount - 1) * ROW_GAP + BOTTOM_PAD : TOP_PAD + BOTTOM_PAD + 40;
  const viewHeight = Math.max(260, contentHeight);
  const midY = peerCount > 0 ? TOP_PAD + ((peerCount - 1) * ROW_GAP) / 2 : viewHeight / 2;

  const nodes: TopologyNode[] = [
    {
      id: 'vpn_server',
      kind: 'vpn_server',
      label: 'VPN server',
      sublabel: data.server.interface,
      detail: `${data.server.gateway_ip}`,
      x: SERVER_X - NODE_W / 2,
      y: midY - NODE_H / 2,
      width: NODE_W,
      height: NODE_H,
    },
    {
      id: 'internet',
      kind: 'internet',
      label: 'Internet',
      sublabel: 'WAN',
      x: INTERNET_X - NODE_W / 2,
      y: midY - NODE_H / 2,
      width: NODE_W,
      height: NODE_H,
    },
  ];

  const edges: TopologyEdge[] = [{ id: 'wan', from: 'vpn_server', to: 'internet' }];

  peers.forEach((peer, index) => {
    const rowY = TOP_PAD + index * ROW_GAP;
    const id = `peer-${peer.peer_id}`;
    const isLiveDns = liveDnsIps.has(peer.client_ip);

    nodes.push({
      id,
      kind: 'vpn_peer',
      label: peerLabel(peer),
      sublabel: peer.client_ip,
      x: CLIENT_X - DOT_R_PEER,
      y: rowY - NODE_H / 2,
      width: NODE_W,
      height: NODE_H,
      handshakeStatus: peer.handshake_status,
      isLiveDns,
      deviceId: peer.device_id ?? undefined,
      href: peer.device_id ? `/client-profiles?device=${peer.device_id}` : undefined,
    });

    edges.push({
      id: `tunnel-${peer.peer_id}`,
      from: id,
      to: 'vpn_server',
    });
  });

  const peerYs = peers.map((_, i) => TOP_PAD + i * ROW_GAP);
  const busY1 = peerYs.length ? Math.min(...peerYs) : midY;
  const busY2 = peerYs.length ? Math.max(...peerYs) : midY;

  return {
    nodes,
    edges,
    serverEndpoint: data.server.endpoint,
    vpnCidr: data.server.cidr,
    gatewayIp: data.server.gateway_ip,
    viewWidth: 800,
    viewHeight,
    layout: {
      clientX: CLIENT_X,
      busX: BUS_X,
      serverX: SERVER_X,
      internetX: INTERNET_X,
      busY1,
      busY2,
      midY,
    },
  };
}

export function peerDotCenter(node: TopologyNode): { x: number; y: number } {
  return { x: node.x + DOT_R_PEER, y: node.y + node.height / 2 };
}

export function hubDotCenter(node: TopologyNode): { x: number; y: number } {
  return { x: node.x + node.width / 2, y: node.y + node.height / 2 };
}
