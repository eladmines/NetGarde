import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import CircularProgress from '@mui/material/CircularProgress';
import RefreshIcon from '@mui/icons-material/Refresh';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import { useDnsAlerts } from '../../dns-queries/hooks/useDnsAlerts';
import { DnsAlert } from '../../dns-queries/types/dnsQuery';
import { formatShortDateTime } from '../../../shared/utils/dateUtils';

const SEVERITY_COLOR: Record<string, 'error' | 'warning' | 'info' | 'default'> = {
  high: 'error',
  medium: 'warning',
  low: 'info',
};

const TYPE_LABEL: Record<string, string> = {
  blocked_attempt: 'Blocked',
  new_domain: 'New site',
  suspicious_domain: 'Suspicious',
  bandwidth_spike: 'Bandwidth',
};

function AlertRow({ alert }: { alert: DnsAlert }) {
  const label = TYPE_LABEL[alert.alert_type] || alert.alert_type;
  const severity = SEVERITY_COLOR[alert.severity] || 'default';

  return (
    <ListItem sx={{ py: 0.75, px: 1.5 }}>
      <ListItemText
        primary={
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
            <Chip label={label} size="small" color={severity} variant="outlined" />
            <Typography variant="body2" sx={{ fontWeight: 600, flex: 1 }}>
              {alert.domain || alert.message || 'Alert'}
            </Typography>
          </Stack>
        }
        secondary={
          <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mt: 0.25, flexWrap: 'wrap' }}>
            <Typography variant="caption" color="text.secondary">
              {formatShortDateTime(alert.timestamp)}
            </Typography>
            {alert.client_ip && (
              <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                {alert.client_ip}
              </Typography>
            )}
            {alert.message && alert.domain && (
              <Typography variant="caption" color="text.secondary">
                {alert.message}
              </Typography>
            )}
          </Stack>
        }
      />
    </ListItem>
  );
}

export default function DnsAlertsView() {
  const { items, total, loading, refetch } = useDnsAlerts();

  return (
    <Paper variant="outlined" sx={{ height: '100%', minHeight: 280, display: 'flex', flexDirection: 'column' }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ px: 2, py: 1.5 }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <WarningAmberIcon color="warning" fontSize="small" />
          <Typography variant="subtitle2">Anomaly Alerts</Typography>
          {total > 0 && <Chip label={total} size="small" color="warning" variant="outlined" />}
        </Stack>
        <Tooltip title="Refresh">
          <IconButton size="small" onClick={refetch} disabled={loading}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>
      <Divider />
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={28} />
          </Box>
        ) : items.length === 0 ? (
          <Typography color="text.secondary" sx={{ p: 2 }}>
            No alerts yet. Blocked attempts, new domains, and bandwidth spikes appear here.
          </Typography>
        ) : (
          <List dense disablePadding>
            {items.map((alert, index) => (
              <Box key={alert.id}>
                <AlertRow alert={alert} />
                {index < items.length - 1 && <Divider component="li" />}
              </Box>
            ))}
          </List>
        )}
      </Box>
    </Paper>
  );
}
