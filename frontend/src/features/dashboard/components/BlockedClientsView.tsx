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
import BlockIcon from '@mui/icons-material/Block';
import { Link as RouterLink } from 'react-router-dom';
import { clientProfilePath } from '../../devices/clientProfilePaths';
import { BlockedClientSummary } from '../../devices/types/device';
import { formatShortDateTime } from '../../../shared/utils/dateUtils';
import { useBlockedClients } from '../hooks/useBlockedClients';

function scoreColor(score: number | null): 'error' | 'warning' | 'default' {
  if (score == null) return 'default';
  if (score >= 85) return 'error';
  if (score >= 70) return 'warning';
  return 'default';
}

function BlockedClientRow({ client }: { client: BlockedClientSummary }) {
  const title = client.hostname || client.client_ip || `Device ${client.device_id}`;
  const meta = [client.client_ip, client.mac_address].filter(Boolean).join(' · ');

  return (
    <ListItemButton
      component={RouterLink}
      to={clientProfilePath(client.device_id)}
      sx={{ py: 1, px: 2, '&:hover': { backgroundColor: 'action.hover' } }}
    >
      <ListItemIcon sx={{ minWidth: 36 }}>
        <BlockIcon color="error" fontSize="small" />
      </ListItemIcon>
      <ListItemText
        primary={
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              {title}
            </Typography>
            {client.last_score != null && (
              <Chip
                label={`Score ${client.last_score}`}
                size="small"
                color={scoreColor(client.last_score)}
                variant="outlined"
                sx={{ height: 22 }}
              />
            )}
            {client.active_block_count > 0 && (
              <Chip
                label={`${client.active_block_count} blocked`}
                size="small"
                color="error"
                variant="filled"
                sx={{ height: 22 }}
              />
            )}
          </Stack>
        }
        secondary={
          <Typography variant="caption" color="text.secondary" component="span" display="block">
            {meta}
            {client.latest_blocked_domain && (
              <>
                {meta ? ' · ' : ''}
                {client.latest_blocked_domain}
              </>
            )}
            {client.latest_block_at && (
              <> · {formatShortDateTime(client.latest_block_at)}</>
            )}
          </Typography>
        }
      />
    </ListItemButton>
  );
}

export default function BlockedClientsView() {
  const { clients, loading, error, refresh } = useBlockedClients();

  return (
    <Paper variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        sx={{ px: 2, py: 1.5 }}
      >
        <Box>
          <Typography variant="subtitle2" fontWeight={600}>
            Blocked clients
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Auto-blocked after abnormal behavior scores
          </Typography>
        </Box>
        <Tooltip title="Refresh">
          <IconButton size="small" onClick={refresh} disabled={loading}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>
      <Divider />
      {error && (
        <Alert severity="error" sx={{ m: 1.5 }}>
          {error}
        </Alert>
      )}
      {loading && clients.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress size={28} />
        </Box>
      ) : clients.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
          No clients are currently auto-blocked.
        </Typography>
      ) : (
        <List dense disablePadding sx={{ overflow: 'auto', flex: 1, maxHeight: 360 }}>
          {clients.map((client) => (
            <BlockedClientRow key={client.device_id} client={client} />
          ))}
        </List>
      )}
    </Paper>
  );
}
