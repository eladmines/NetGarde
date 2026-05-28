import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { DOT_R_INTERNET, DOT_R_PEER, DOT_R_SERVER } from '../topology/buildVpnTopology';
import { TopologyNode, VpnHandshakeStatus } from '../topology/types';

function dotColor(kind: TopologyNode['kind'], hs?: VpnHandshakeStatus): string {
  if (kind === 'vpn_peer') {
    if (hs === 'connected') return '#2e7d32';
    return '#9e9e9e';
  }
  if (kind === 'vpn_server') return '#3949ab';
  return '#78909c';
}

function dotRadius(kind: TopologyNode['kind']): number {
  if (kind === 'vpn_server') return DOT_R_SERVER;
  if (kind === 'internet') return DOT_R_INTERNET;
  return DOT_R_PEER;
}

interface TopologyDotNodeProps {
  node: TopologyNode;
  onSelect?: (node: TopologyNode) => void;
}

export default function TopologyDotNode({ node, onSelect }: TopologyDotNodeProps) {
  const isPeer = node.kind === 'vpn_peer';
  const r = dotRadius(node.kind);
  const fill = dotColor(node.kind, node.handshakeStatus);
  const clickable = isPeer && node.deviceId != null && onSelect != null;

  if (isPeer) {
    return (
      <Box
        component={clickable ? 'button' : 'div'}
        type={clickable ? 'button' : undefined}
        onClick={clickable ? () => onSelect!(node) : undefined}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          border: 'none',
          background: 'none',
          cursor: clickable ? 'pointer' : 'default',
          p: 0,
          textAlign: 'left',
          '&:hover': clickable ? { opacity: 0.85 } : {},
        }}
      >
        <Box
          component="span"
          sx={{
            width: r * 2,
            height: r * 2,
            borderRadius: '50%',
            bgcolor: fill,
            flexShrink: 0,
            boxShadow: node.handshakeStatus === 'connected' ? '0 0 0 3px rgba(46,125,50,0.2)' : 'none',
          }}
        />
        <Box sx={{ minWidth: 0 }}>
          <Typography variant="body2" fontWeight={600} noWrap sx={{ maxWidth: 160 }}>
            {node.label}
          </Typography>
          {node.sublabel && (
            <Typography variant="caption" color="text.secondary" display="block">
              {node.sublabel}
            </Typography>
          )}
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
      <Box
        component="span"
        sx={{
          width: r * 2,
          height: r * 2,
          borderRadius: '50%',
          bgcolor: fill,
          boxShadow: 1,
        }}
      />
      <Typography variant="caption" fontWeight={600}>
        {node.label}
      </Typography>
      {node.sublabel && (
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
          {node.sublabel}
        </Typography>
      )}
      {node.detail && (
        <Typography variant="caption" color="secondary.main" sx={{ fontSize: '0.65rem' }}>
          {node.detail}
        </Typography>
      )}
    </Box>
  );
}
