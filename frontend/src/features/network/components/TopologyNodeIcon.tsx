import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CloudIcon from '@mui/icons-material/Cloud';
import RouterIcon from '@mui/icons-material/Router';
import LaptopMacIcon from '@mui/icons-material/LaptopMac';
import DevicesOtherIcon from '@mui/icons-material/DevicesOther';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import { TopologyNode, VpnHandshakeStatus } from '../topology/types';

const ICON_SIZE = 32;
const BADGE_SIZE = 56;

function peerStatus(hs: VpnHandshakeStatus | undefined): 'up' | 'idle' | 'down' {
  if (hs === 'connected') return 'up';
  if (hs === 'idle') return 'idle';
  return 'down';
}

const BORDER_COLOR = {
  up: 'success.main',
  idle: 'warning.main',
  down: 'grey.400',
} as const;

function NodeIcon({ node }: { node: TopologyNode }) {
  const sx = { fontSize: ICON_SIZE };
  switch (node.kind) {
    case 'internet':
      return <CloudIcon sx={{ ...sx, color: 'primary.main' }} />;
    case 'vpn_server':
      return <RouterIcon sx={{ ...sx, color: 'secondary.main' }} />;
    case 'vpn_peer':
      return node.label.toLowerCase().includes('iphone') || node.label.toLowerCase().includes('ipad') ? (
        <DevicesOtherIcon sx={sx} />
      ) : (
        <LaptopMacIcon sx={sx} />
      );
    default:
      return <DevicesOtherIcon sx={sx} />;
  }
}

function truncate(text: string, max: number): string {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

interface TopologyNodeIconProps {
  node: TopologyNode;
  onSelect?: (node: TopologyNode) => void;
}

export default function TopologyNodeIcon({ node, onSelect }: TopologyNodeIconProps) {
  const isPeer = node.kind === 'vpn_peer';
  const status = isPeer ? peerStatus(node.handshakeStatus) : 'up';
  const borderColor = isPeer ? BORDER_COLOR[status] : 'primary.light';
  const clickable = isPeer && node.deviceId != null && onSelect != null;

  return (
    <Box
      component={clickable ? 'button' : 'div'}
      type={clickable ? 'button' : undefined}
      onClick={clickable ? () => onSelect!(node) : undefined}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 0.5,
        width: node.width,
        border: 'none',
        background: 'none',
        cursor: clickable ? 'pointer' : 'default',
        p: 0,
        '&:hover': clickable ? { opacity: 0.92 } : {},
      }}
    >
      <Box
        sx={{
          width: BADGE_SIZE,
          height: BADGE_SIZE,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.paper',
          border: 2,
          borderColor,
          boxShadow: 1,
          position: 'relative',
        }}
      >
        <NodeIcon node={node} />
        {isPeer && (
          <FiberManualRecordIcon
            sx={{
              position: 'absolute',
              bottom: 2,
              right: 2,
              fontSize: 14,
              color: BORDER_COLOR[status],
            }}
          />
        )}
        {isPeer && node.isLiveDns && (
          <FiberManualRecordIcon
            sx={{
              position: 'absolute',
              top: 2,
              left: 2,
              fontSize: 12,
              color: 'info.main',
            }}
          />
        )}
      </Box>
      <Typography variant="caption" fontWeight={600} textAlign="center" lineHeight={1.2}>
        {truncate(node.label, 18)}
      </Typography>
      {node.sublabel && (
        <Typography variant="caption" color="text.secondary" textAlign="center" lineHeight={1.2}>
          {truncate(node.sublabel, 22)}
        </Typography>
      )}
      {node.detail && isPeer && (
        <Typography variant="caption" color="text.disabled" textAlign="center" sx={{ fontSize: '0.65rem' }}>
          {truncate(node.detail, 26)}
        </Typography>
      )}
      {node.kind === 'vpn_server' && node.detail && (
        <Typography variant="caption" color="secondary.main" textAlign="center" sx={{ fontSize: '0.65rem' }}>
          {truncate(node.detail, 30)}
        </Typography>
      )}
    </Box>
  );
}

export { BADGE_SIZE };
