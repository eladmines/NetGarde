import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom';
import type { CSSProperties } from 'react';
import { hubDotCenter, peerDotCenter } from '../topology/buildVpnTopology';
import { TopologyNode, VpnTopologyGraph } from '../topology/types';
import TopologyDotNode from './TopologyDotNode';

function toPercentX(x: number, viewW: number): string {
  return `${(x / viewW) * 100}%`;
}

function toPercentY(y: number, viewH: number): string {
  return `${(y / viewH) * 100}%`;
}

function nodePositionStyle(node: TopologyNode, viewW: number, viewH: number): CSSProperties {
  if (node.kind === 'vpn_peer') {
    return {
      position: 'absolute',
      left: toPercentX(node.x, viewW),
      top: toPercentY(node.y, viewH),
      transform: 'translate(0, -50%)',
      zIndex: 2,
    };
  }
  const cx = node.x + node.width / 2;
  const cy = node.y + node.height / 2;
  return {
    position: 'absolute',
    left: toPercentX(cx, viewW),
    top: toPercentY(cy, viewH),
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
  const { layout, viewWidth, viewHeight } = topology;

  const server = nodeById.get('vpn_server');
  const internet = nodeById.get('internet');
  const peers = topology.nodes.filter((n) => n.kind === 'vpn_peer');

  const handleSelect = (node: TopologyNode) => {
    if (node.href) navigate(node.href);
  };

  const serverCenter = server ? hubDotCenter(server) : { x: layout.serverX, y: layout.midY };
  const internetCenter = internet ? hubDotCenter(internet) : { x: layout.internetX, y: layout.midY };

  return (
    <Box
      sx={{
        width: '100%',
        position: 'relative',
        borderRadius: 1,
        bgcolor: 'grey.50',
        border: 1,
        borderColor: 'divider',
        minHeight: 220,
        aspectRatio: `${viewWidth} / ${viewHeight}`,
        maxHeight: 480,
      }}
    >
      <Box
        component="svg"
        viewBox={`0 0 ${viewWidth} ${viewHeight}`}
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
        aria-label="VPN topology: clients on the left, network on the right"
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

        <text x={24} y={28} fontSize={11} fill="#757575" fontWeight={600}>
          Clients
        </text>
        <text x={layout.serverX - 36} y={28} fontSize={11} fill="#757575" fontWeight={600}>
          Network
        </text>

        {peers.length > 0 && (
          <line
            x1={layout.busX}
            y1={layout.busY1}
            x2={layout.busX}
            y2={layout.busY2}
            stroke="#bdbdbd"
            strokeWidth={2}
          />
        )}

        {peers.map((peer) => {
          const { x: px, y: py } = peerDotCenter(peer);
          const connected = peer.handshakeStatus === 'connected';
          const stroke = connected ? '#43a047' : '#bdbdbd';
          const width = connected ? 2.5 : 1.5;
          const dash = connected ? undefined : '6 4';
          return (
            <g key={`link-${peer.id}`}>
              <path
                d={`M ${px + 9} ${py} H ${layout.busX} V ${serverCenter.y} H ${serverCenter.x - 14}`}
                fill="none"
                stroke={stroke}
                strokeWidth={width}
                strokeDasharray={dash}
              />
            </g>
          );
        })}

        <line
          x1={serverCenter.x + 14}
          y1={serverCenter.y}
          x2={internetCenter.x - 12}
          y2={internetCenter.y}
          stroke="#78909c"
          strokeWidth={2}
          markerEnd="url(#vpn-arrow)"
        />
      </Box>

      {topology.nodes.map((node) => (
        <Box key={node.id} sx={nodePositionStyle(node, viewWidth, viewHeight)}>
          <TopologyDotNode node={node} onSelect={handleSelect} />
        </Box>
      ))}

      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ position: 'absolute', left: 12, bottom: 8, zIndex: 2, fontSize: '0.7rem' }}
      >
        {topology.vpnCidr} · Gateway {topology.gatewayIp}
      </Typography>
    </Box>
  );
}
