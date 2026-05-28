import Box from '@mui/material/Box';
import { useNavigate } from 'react-router-dom';
import { edgePath, nodeAnchor } from '../topology/buildNetworkTopology';
import { NetworkTopology, TopologyNode } from '../topology/types';

const KIND_COLORS: Record<string, { fill: string; stroke: string }> = {
  internet: { fill: '#e3f2fd', stroke: '#1976d2' },
  gateway: { fill: '#e8eaf6', stroke: '#3949ab' },
  dns: { fill: '#fff3e0', stroke: '#ef6c00' },
  api: { fill: '#e8f5e9', stroke: '#2e7d32' },
  database: { fill: '#fce4ec', stroke: '#c2185b' },
  log_ingest: { fill: '#f3e5f5', stroke: '#7b1fa2' },
  client: { fill: '#fafafa', stroke: '#9e9e9e' },
};

function NodeBox({ node, onSelect }: { node: TopologyNode; onSelect?: (node: TopologyNode) => void }) {
  const colors = KIND_COLORS[node.kind] ?? KIND_COLORS.client;
  const stroke = node.isLive ? '#2e7d32' : colors.stroke;
  const strokeWidth = node.isLive ? 2.5 : 1.5;
  const clickable = node.deviceId != null && onSelect != null;

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
        fill={node.isLive ? '#e8f5e9' : colors.fill}
        stroke={stroke}
        strokeWidth={strokeWidth}
      />
      {node.isLive && (
        <circle cx={node.width - 10} cy={10} r={5} fill="#2e7d32" />
      )}
      <text
        x={node.width / 2}
        y={node.height / 2 - (node.sublabel ? 6 : 0)}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={12}
        fontWeight={600}
        fill="#212121"
      >
        {truncate(node.label, 14)}
      </text>
      {node.sublabel && (
        <text
          x={node.width / 2}
          y={node.height / 2 + 12}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={10}
          fill="#616161"
        >
          {truncate(node.sublabel, 18)}
        </text>
      )}
    </g>
  );
}

function truncate(text: string, max: number): string {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

interface NetworkTopologyGraphProps {
  topology: NetworkTopology;
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
        viewBox="0 0 800 440"
        width="100%"
        height="auto"
        style={{ display: 'block', minHeight: 360 }}
        role="img"
        aria-label="NetGarde network topology"
      >
        <defs>
          <marker
            id="arrow"
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="4"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L8,4 L0,8 Z" fill="#90a4ae" />
          </marker>
        </defs>

        {topology.edges.map((edge) => {
          const from = nodeById.get(edge.from);
          const to = nodeById.get(edge.to);
          if (!from || !to) return null;
          const d = edgePath(from, to);
          const mid = labelMidpoint(from, to);
          return (
            <g key={edge.id}>
              <path
                d={d}
                fill="none"
                stroke={edge.dashed ? '#b0bec5' : '#78909c'}
                strokeWidth={1.5}
                strokeDasharray={edge.dashed ? '6 4' : undefined}
                markerEnd="url(#arrow)"
              />
              {edge.label && (
                <text x={mid.x} y={mid.y} fontSize={9} fill="#607d8b" textAnchor="middle">
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}

        {topology.nodes.map((node) => (
          <NodeBox key={node.id} node={node} onSelect={handleSelect} />
        ))}

        <text x={16} y={430} fontSize={10} fill="#757575">
          VPN subnet {topology.vpnCidr} · Gateway {topology.gatewayIp} · Green = live DNS activity
        </text>
      </svg>
    </Box>
  );
}

function labelMidpoint(from: TopologyNode, to: TopologyNode): { x: number; y: number } {
  const a = nodeAnchor(from, 'bottom');
  const b = nodeAnchor(to, 'top');
  return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
}
