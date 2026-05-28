import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Chip from '@mui/material/Chip';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useNetworkTopology } from '../hooks/useNetworkTopology';
import NetworkTopologyGraph from './NetworkTopologyGraph';

export default function NetworkTopologyView() {
  const { topology, loading, error, liveCount, clientCount, refresh } = useNetworkTopology();

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        flexWrap="wrap"
        gap={1}
        sx={{ mb: 2 }}
      >
        <Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Network topology
          </Typography>
          <Typography variant="body2" color="text.secondary">
            How traffic flows from clients through the VPN gateway, DNS filtering, and API.
          </Typography>
        </Box>
        <Stack direction="row" spacing={1} alignItems="center">
          {clientCount > 0 && (
            <Chip
              size="small"
              label={`${liveCount} live / ${clientCount} registered`}
              color={liveCount > 0 ? 'success' : 'default'}
              variant="outlined"
            />
          )}
          <Tooltip title="Refresh">
            <IconButton size="small" onClick={refresh} disabled={loading}>
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading && !topology ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : topology ? (
        <NetworkTopologyGraph topology={topology} />
      ) : null}

      <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mt: 2 }}>
        <LegendSwatch label="Internet / WAN" color="#1976d2" />
        <LegendSwatch label="Gateway & services" color="#3949ab" />
        <LegendSwatch label="VPN client (live)" color="#2e7d32" />
        <LegendSwatch label="VPN client (idle)" color="#9e9e9e" />
      </Stack>
    </Paper>
  );
}

function LegendSwatch({ label, color }: { label: string; color: string }) {
  return (
    <Stack direction="row" spacing={0.75} alignItems="center">
      <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: color }} />
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
    </Stack>
  );
}
