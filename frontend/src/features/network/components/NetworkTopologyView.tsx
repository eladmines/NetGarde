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
  const { topology, loading, error, connectedCount, peerCount, refresh } = useNetworkTopology();

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
            VPN topology
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Clients on the left connect only to the VPN server — not to each other.
          </Typography>
        </Box>
        <Stack direction="row" spacing={1} alignItems="center">
          {peerCount > 0 && (
            <Chip
              size="small"
              label={`${connectedCount} connected / ${peerCount} enrolled`}
              color={connectedCount > 0 ? 'success' : 'default'}
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

      <Stack direction="row" flexWrap="wrap" gap={2} sx={{ mt: 2 }}>
        <LegendSwatch label="Connected" color="#2e7d32" />
        <LegendSwatch label="Not connected" color="#9e9e9e" />
        <LegendSwatch label="VPN server" color="#3949ab" />
        <LegendSwatch label="Internet" color="#78909c" />
      </Stack>
    </Paper>
  );
}

function LegendSwatch({ label, color }: { label: string; color: string }) {
  return (
    <Stack direction="row" spacing={0.75} alignItems="center">
      <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: color }} />
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
    </Stack>
  );
}
