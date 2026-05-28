import { Device } from '../../devices/types/device';
import { NetworkTopology, TopologyEdge, TopologyNode } from './types';

const VPN_CIDR = '10.0.0.0/24';
const GATEWAY_IP = '10.0.0.1';

const NODE_W = 128;
const NODE_H = 52;
const CLIENT_W = 118;
const CLIENT_H = 48;

function infraNode(
  id: string,
  kind: TopologyNode['kind'],
  label: string,
  sublabel: string | undefined,
  x: number,
  y: number,
): TopologyNode {
  return { id, kind, label, sublabel, x, y, width: NODE_W, height: NODE_H };
}

function clientPositions(count: number, centerX: number, y: number): { x: number }[] {
  if (count === 0) return [];
  if (count === 1) return [{ x: centerX - CLIENT_W / 2 }];
  const span = Math.min(560, 140 * (count - 1));
  const startX = centerX - span / 2 - CLIENT_W / 2;
  const step = count > 1 ? span / (count - 1) : 0;
  return Array.from({ length: count }, (_, i) => ({ x: startX + i * step }));
}

export function buildNetworkTopology(
  devices: Device[],
  liveClientIps: Set<string>,
): NetworkTopology {
  const centerX = 400;
  const nodes: TopologyNode[] = [
    infraNode('internet', 'internet', 'Internet', 'WAN', centerX - NODE_W / 2, 24),
    infraNode('gateway', 'gateway', 'NetGarde Gateway', `WireGuard · ${GATEWAY_IP}`, centerX - NODE_W / 2, 108),
    infraNode('dns', 'dns', 'DNS (dnsmasq)', 'Filtering + blocklist', centerX - NODE_W - 48, 208),
    infraNode('api', 'api', 'API', 'Policy & devices', centerX - NODE_W / 2, 248),
    infraNode('log_ingest', 'log_ingest', 'Log watcher', 'DNS ingest', centerX + 48, 208),
    infraNode('database', 'database', 'Database', 'RDS / Postgres', centerX + NODE_W + 20, 208),
  ];

  const edges: TopologyEdge[] = [
    { id: 'wan', from: 'internet', to: 'gateway', label: 'UDP 51820' },
    { id: 'gw-dns', from: 'gateway', to: 'dns' },
    { id: 'gw-api', from: 'gateway', to: 'api' },
    { id: 'gw-log', from: 'gateway', to: 'log_ingest' },
    { id: 'api-db', from: 'api', to: 'database', dashed: true },
    { id: 'log-api', from: 'log_ingest', to: 'api', label: 'bulk ingest', dashed: true },
    { id: 'dns-api', from: 'dns', to: 'api', dashed: true },
  ];

  const vpnClients = devices.filter((d) => d.client_ip.startsWith('10.0.0.'));
  const otherDevices = devices.filter((d) => !d.client_ip.startsWith('10.0.0.'));
  const ordered = [...vpnClients, ...otherDevices];
  const positions = clientPositions(ordered.length, centerX, 368);

  ordered.forEach((device, index) => {
    const id = `client-${device.id}`;
    const isLive = liveClientIps.has(device.client_ip);
    const pos = positions[index] ?? { x: centerX - CLIENT_W / 2 };
    nodes.push({
      id,
      kind: 'client',
      label: device.hostname || device.client_ip,
      sublabel: device.client_ip,
      x: pos.x,
      y: 368,
      width: CLIENT_W,
      height: CLIENT_H,
      isLive,
      deviceId: device.id,
      href: `/client-profiles?device=${device.id}`,
    });
    edges.push({
      id: `tunnel-${device.id}`,
      from: 'gateway',
      to: id,
      label: device.source === 'vpn_enroll' ? 'VPN' : undefined,
    });
    edges.push({ id: `dns-${device.id}`, from: id, to: 'dns', dashed: true });
  });

  return { nodes, edges, vpnCidr: VPN_CIDR, gatewayIp: GATEWAY_IP };
}

/** Center point on the bottom edge of a node (for edges). */
export function nodeAnchor(node: TopologyNode, side: 'top' | 'bottom' | 'left' | 'right'): { x: number; y: number } {
  const cx = node.x + node.width / 2;
  const cy = node.y + node.height / 2;
  switch (side) {
    case 'top':
      return { x: cx, y: node.y };
    case 'bottom':
      return { x: cx, y: node.y + node.height };
    case 'left':
      return { x: node.x, y: cy };
    case 'right':
      return { x: node.x + node.width, y: cy };
    default:
      return { x: cx, y: cy };
  }
}

export function edgePath(from: TopologyNode, to: TopologyNode): string {
  const a =
    from.kind === 'internet' || from.kind === 'gateway'
      ? nodeAnchor(from, 'bottom')
      : nodeAnchor(from, from.y < to.y ? 'bottom' : 'top');
  const b =
    to.kind === 'client'
      ? nodeAnchor(to, 'top')
      : to.kind === 'internet'
        ? nodeAnchor(to, 'top')
        : nodeAnchor(to, to.y > from.y ? 'top' : 'bottom');

  const midY = (a.y + b.y) / 2;
  return `M ${a.x} ${a.y} C ${a.x} ${midY}, ${b.x} ${midY}, ${b.x} ${b.y}`;
}
