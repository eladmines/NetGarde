import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom';
import type { CSSProperties } from 'react';
import { edgeEndpoints, VIEWBOX_H, VIEWBOX_W, vpnSubnetBounds } from '../topology/buildVpnTopology';
import { TopologyNode, VpnTopologyGraph } from '../topology/types';
import TopologyNodeIcon from './TopologyNodeIcon';

function toPercentX(x: number): string {
  return `${(x / VIEWBOX_W) * 100}%`;
}

function toPercentY(y: number): string {
  return `${(y / VIEWBOX_H) * 100}%`;
}

function nodePositionStyle(node: TopologyNode): CSSProperties {
  const cx = node.x + node.width / 2;
  const cy = node.y + node.height / 2;
  return {
    position: 'absolute',
    left: toPercentX(cx),
    top: toPercentY(cy),
    transform: 'translate(-50%, -50%)',
    zIndex: 2,
  };
}

interface NetworkTopologyGraphProps {
  topology: VpnTopologyGraph;
}

export default function NetworkTopologyGraph({ topology }: NetworkTopologyGraphProps) {
  const navigate = useNavigate();
  const nodeById = new Map(topology.nodes.map((n) => [n.id, n]));
  const subnet = vpnSubnetBounds(topology.nodes);

  const handleSelect = (node: TopologyNode) => {
    if (node.href) navigate(node.href);
  };

  return (
    <Box
      sx={{
        width: '100%',
        position: 'relative',
        borderRadius: 1,
        bgcolor: 'grey.50',
        border: 1,
        borderColor: 'divider',
        minHeight: 380,
        aspectRatio: `${VIEWBOX_W} / ${VIEWBOX_H}`,
        maxHeight: 520,
      }}
    >
      <Box
        component="svg"
        viewBox={`0 0 ${VIEWBOX_W} ${VIEWBOX_H}`}
        preserveAspectRatio="xMidYMid meet"
        sx={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          display: 'block',
          zIndex: 1,
        }}
        role="img"
        aria-hidden
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

        {subnet && (
          <g>
            <rect
              x={subnet.x}
              y={subnet.y}
              width={subnet.width}
              height={subnet.height}
              rx={14}
              fill="rgba(92, 107, 192, 0.04)"
              stroke="#9fa8da"
              strokeWidth={1.5}
              strokeDasharray="8 5"
            />
            <text x={subnet.x + 14} y={subnet.y + 20} fontSize={11} fill="#5c6bc0" fontWeight={600}>
              {topology.vpnCidr} · WireGuard VPN
            </text>
          </g>
        )}

        {topology.edges.map((edge) => {
          const from = nodeById.get(edge.from);
          const to = nodeById.get(edge.to);
          if (!from || !to) return null;
          const { x1, y1, x2, y2 } = edgeEndpoints(from, to);
          const mx = (x1 + x2) / 2;
          const my = (y1 + y2) / 2;
          const connected = to.handshakeStatus === 'connected';
          const isWan = edge.from === 'internet';
          return (
            <g key={edge.id}>
              <line
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={connected ? '#43a047' : isWan ? '#78909c' : '#90a4ae'}
                strokeWidth={connected ? 2.5 : isWan ? 2 : 1.5}
                strokeDasharray={connected || isWan ? undefined : '6 4'}
                markerEnd="url(#vpn-arrow)"
              />
              {edge.label && (
                <text x={mx} y={my - 8} fontSize={10} fill="#607d8b" textAnchor="middle">
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}
      </Box>

      {topology.nodes.map((node) => (
        <Box key={node.id} sx={nodePositionStyle(node)}>
          <TopologyNodeIcon node={node} onSelect={handleSelect} />
        </Box>
      ))}

      <Typography
        variant="caption"
        color="text.secondary"
        sx={{
          position: 'absolute',
          left: 12,
          bottom: 8,
          zIndex: 2,
          fontSize: '0.7rem',
        }}
      >
        Gateway {topology.gatewayIp} · Endpoint {topology.serverEndpoint}
      </Typography>
    </Box>
  );
}
