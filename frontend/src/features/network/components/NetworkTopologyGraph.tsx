import Box from '@mui/material/Box';
import { useNavigate } from 'react-router-dom';
import { edgeEndpoints } from '../topology/buildVpnTopology';
import { TopologyNode, VpnTopologyGraph, VpnHandshakeStatus } from '../topology/types';

const KIND_STYLES: Record<string, { fill: string; stroke: string }> = {
  internet: { fill: '#e3f2fd', stroke: '#1565c0' },
  vpn_server: { fill: '#e8eaf6', stroke: '#283593' },
};

const PEER_STROKE: Record<VpnHandshakeStatus, string> = {
  connected: '#2e7d32',
  idle: '#ed6c02',
  never: '#9e9e9e',
  unknown: '#757575',
};

const PEER_FILL: Record<VpnHandshakeStatus, string> = {
  connected: '#e8f5e9',
  idle: '#fff3e0',
  never: '#fafafa',
  unknown: '#f5f5f5',
};

function NodeBox({ node, onSelect }: { node: TopologyNode; onSelect?: (node: TopologyNode) => void }) {
  const isPeer = node.kind === 'vpn_peer';
  const hs = node.handshakeStatus ?? 'unknown';
  const colors = isPeer ? { fill: PEER_FILL[hs], stroke: PEER_STROKE[hs] } : KIND_STYLES[node.kind];
  const strokeWidth = hs === 'connected' ? 2.5 : 1.5;
  const clickable = isPeer && node.deviceId != null && onSelect != null;

  return (
    <g
      transform={`translate(${node.x}, ${node.y})`}
      onClick={clickable ? () => onSelect!(node) : undefined}
      style={clickable ? { cursor: 'pointer' } : undefined}
      role={clickable ? 'button' : undefined}
      tabIndex={clickable ? 0 : undefined}
      onKeyDown={
        clickable
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') onSelect!(node);
            }
          : undefined
      }
    >
      <rect
        width={node.width}
        height={node.height}
        rx={8}
        fill={colors.fill}
        stroke={colors.stroke}
        strokeWidth={strokeWidth}
      />
      {isPeer && hs === 'connected' && (
        <circle cx={node.width - 10} cy={10} r={5} fill="#2e7d32" />
      )}
      {isPeer && node.isLiveDns && (
        <circle cx={10} cy={10} r={5} fill="#1976d2" />
      )}
      <text
        x={node.width / 2}
        y={node.height / 2 - (node.detail ? 8 : node.sublabel ? 4 : 0)}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={isPeer ? 11 : 12}
        fontWeight={600}
        fill="#212121"
      >
        {truncate(node.label, 16)}
      </text>
      {node.sublabel && (
        <text
          x={node.width / 2}
          y={node.height / 2 + 8}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={10}
          fill="#616161"
        >
          {truncate(node.sublabel, 20)}
        </text>
      )}
      {node.detail && isPeer && (
        <text
          x={node.width / 2}
          y={node.height / 2 + 20}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={9}
          fill="#757575"
        >
          {truncate(node.detail, 24)}
        </text>
      )}
      {node.kind === 'vpn_server' && node.detail && (
        <text
          x={node.width / 2}
          y={node.height - 8}
          textAnchor="middle"
          fontSize={9}
          fill="#5c6bc0"
        >
          {truncate(node.detail, 28)}
        </text>
      )}
    </g>
  );
}

function truncate(text: string, max: number): string {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

interface NetworkTopologyGraphProps {
  topology: VpnTopologyGraph;
}

export default function NetworkTopologyGraph({ topology }: NetworkTopologyGraphProps) {
  const navigate = useNavigate();
  const nodeById = new Map(topology.nodes.map((n) => [n.id, n]));

  const handleSelect = (node: TopologyNode) => {
    if (node.href) navigate(node.href);
  };

  return (
    <Box
      sx={{
        width: '100%',
        overflow: 'auto',
        borderRadius: 1,
        bgcolor: 'grey.50',
        border: 1,
        borderColor: 'divider',
      }}
    >
      <svg
        viewBox="0 0 800 420"
        width="100%"
        height="auto"
        style={{ display: 'block', minHeight: 360 }}
        role="img"
        aria-label="WireGuard VPN topology"
      >
        <defs>
          <marker
            id="vpn-arrow"
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="4"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L8,4 L0,8 Z" fill="#78909c" />
          </marker>
        </defs>

        {topology.edges.map((edge) => {
          const from = nodeById.get(edge.from);
          const to = nodeById.get(edge.to);
          if (!from || !to) return null;
          const { x1, y1, x2, y2 } = edgeEndpoints(from, to);
          const mx = (x1 + x2) / 2;
          const my = (y1 + y2) / 2;
          const connected = to.handshakeStatus === 'connected';
          return (
            <g key={edge.id}>
              <line
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={connected ? '#43a047' : '#90a4ae'}
                strokeWidth={connected ? 2 : 1.5}
                strokeDasharray={connected ? undefined : '6 4'}
                markerEnd="url(#vpn-arrow)"
              />
              {edge.label && (
                <text x={mx} y={my - 6} fontSize={9} fill="#607d8b" textAnchor="middle">
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}

        {topology.nodes.map((node) => (
          <NodeBox key={node.id} node={node} onSelect={handleSelect} />
        ))}

        <text x={16} y={408} fontSize={10} fill="#757575">
          Pool {topology.vpnCidr} · Gateway {topology.gatewayIp} · Endpoint {topology.serverEndpoint}
        </text>
      </svg>
    </Box>
  );
}
