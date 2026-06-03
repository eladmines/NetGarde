import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import RefreshIcon from '@mui/icons-material/Refresh';
import DevicesIcon from '@mui/icons-material/Devices';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import LinearProgress from '@mui/material/LinearProgress';
import { Link as RouterLink } from 'react-router-dom';
import { clientProfilePath } from '../../devices/clientProfilePaths';
import {
  formatClientSource,
  LiveClientRow,
  useLiveClients,
} from '../hooks/useLiveClients';
import { formatBytesCompact, formatMibPerSec } from '../utils/formatBandwidth';
import LiveNetworkGraph from './LiveNetworkGraph';

function BandwidthChips({ client }: { client: LiveClientRow }) {
  const bw = client.bandwidth;
  if (!bw || bw.total_mib_per_sec <= 0) {
    if (client.source === 'vpn_enroll') {
      return (
        <Typography variant="caption" color="text.secondary">
          No VPN traffic sample — use{' '}
          <Typography component="span" variant="caption" sx={{ fontFamily: 'monospace' }}>
            --stats-interval 5
          </Typography>{' '}
          on netgarde-wg
        </Typography>
      );
    }
    return null;
  }

  const maxRate = Math.max(bw.rx_mib_per_sec, bw.tx_mib_per_sec, 0.01);
  const downPct = Math.min(100, (bw.rx_mib_per_sec / maxRate) * 100);
  const upPct = Math.min(100, (bw.tx_mib_per_sec / maxRate) * 100);

  return (
    <Stack spacing={0.75} sx={{ mt: 0.75, width: '100%' }}>
      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap alignItems="center">
        <Chip
          size="small"
          variant="outlined"
          icon={<ArrowDownwardIcon sx={{ fontSize: '14px !important' }} />}
          label={`${formatMibPerSec(bw.rx_mib_per_sec)} MiB/s`}
          sx={{ height: 24 }}
        />
        <Chip
          size="small"
          variant="outlined"
          icon={<ArrowUpwardIcon sx={{ fontSize: '14px !important' }} />}
          label={`${formatMibPerSec(bw.tx_mib_per_sec)} MiB/s`}
          sx={{ height: 24 }}
        />
        <Typography variant="caption" color="text.secondary">
          +{formatBytesCompact(bw.delta_rx_bytes)} ↓ / +{formatBytesCompact(bw.delta_tx_bytes)} ↑
          last interval
        </Typography>
      </Stack>
      <Stack direction="row" spacing={1} alignItems="center">
        <Typography variant="caption" color="text.secondary" sx={{ minWidth: 28 }}>
          ↓
        </Typography>
        <LinearProgress
          variant="determinate"
          value={downPct}
          sx={{ flex: 1, height: 6, borderRadius: 1 }}
        />
        <Typography variant="caption" color="text.secondary" sx={{ minWidth: 28 }}>
          ↑
        </Typography>
        <LinearProgress
          variant="determinate"
          value={upPct}
          color="secondary"
          sx={{ flex: 1, height: 6, borderRadius: 1 }}
        />
      </Stack>
    </Stack>
  );
}

function ClientRow({ client }: { client: LiveClientRow }) {
  const title = client.hostname || client.client_ip;
  const subtitleParts = [client.client_ip];
  if (client.mac_address) subtitleParts.push(client.mac_address);
  if (client.source) subtitleParts.push(formatClientSource(client.source));

  if (client.device_id == null) {
    return null;
  }

  return (
    <ListItemButton
      component={RouterLink}
      to={clientProfilePath(client.device_id)}
      sx={{
        py: 1,
        px: 2,
        '&:hover': { backgroundColor: 'action.hover' },
      }}
    >
      <ListItemIcon sx={{ minWidth: 36 }}>
        {client.source === 'vpn_enroll' ? (
          <VpnKeyIcon color="primary" fontSize="small" />
        ) : (
          <DevicesIcon color="action" fontSize="small" />
        )}
      </ListItemIcon>
      <ListItemText
        primary={
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              {title}
            </Typography>
            <Chip
              icon={<FiberManualRecordIcon sx={{ fontSize: '10px !important' }} />}
              label="Live"
              size="small"
              color="success"
              variant="outlined"
              sx={{ height: 22, '& .MuiChip-icon': { color: 'success.main' } }}
            />
          </Stack>
        }
        secondary={
          <Box component="span" sx={{ display: 'block' }}>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.25, display: 'block' }}>
              {subtitleParts.join(' · ')}
            </Typography>
            <BandwidthChips client={client} />
          </Box>
        }
      />
    </ListItemButton>
  );
}

export default function LiveClientsView() {
  const {
    clients,
    loading,
    error,
    usageError,
    enrolledCount,
    serverThroughput,
    throughputHistory,
    refetch,
  } = useLiveClients();

  if (loading && clients.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper variant="outlined" sx={{ maxHeight: 720, display: 'flex', flexDirection: 'column' }}>
      <Stack
        direction="row"
        alignItems="center"
        spacing={1}
        sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: 'divider', flexWrap: 'wrap' }}
      >
        <Typography variant="body2" color="text.secondary">
          {clients.length === 0
            ? 'No clients connected'
            : `${clients.length} connected client${clients.length === 1 ? '' : 's'}`}
          {enrolledCount > 0 && ` · ${enrolledCount} VPN enrolled`}
          {serverThroughput.reporting_clients > 0 &&
            ` · server ${formatMibPerSec(serverThroughput.total_mib_per_sec)} MiB/s`}
        </Typography>
        <Box sx={{ flex: 1 }} />
        <Tooltip title="Refresh">
          <IconButton size="small" onClick={refetch} disabled={loading}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>

      {error && (
        <Alert severity="warning" sx={{ mx: 2, mt: 1 }}>
          {error}
        </Alert>
      )}
      <LiveNetworkGraph
        serverThroughput={serverThroughput}
        history={throughputHistory}
        usageError={usageError}
      />

      {usageError && (
        <Alert severity="info" sx={{ mx: 2, mt: 1 }}>
          Bandwidth: {usageError}
        </Alert>
      )}

      <Typography variant="subtitle2" sx={{ px: 2, pt: 1, pb: 0.5 }}>
        Connected clients
      </Typography>

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {clients.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: 200,
              color: 'text.secondary',
              px: 2,
              textAlign: 'center',
            }}
          >
            <Typography variant="body2">
              No clients are sending DNS through the VPN right now. Connect with the NetGarde client
              and browse to appear here.
            </Typography>
          </Box>
        ) : (
          <List dense disablePadding>
            {clients.map((client, index) => (
              <Box key={client.client_ip}>
                <ClientRow client={client} />
                {index < clients.length - 1 && <Divider component="li" />}
              </Box>
            ))}
          </List>
        )}
      </Box>
    </Paper>
  );
}
