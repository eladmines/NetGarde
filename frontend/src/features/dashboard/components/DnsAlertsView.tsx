import { useState } from 'react';
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
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import RefreshIcon from '@mui/icons-material/Refresh';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import SearchIcon from '@mui/icons-material/Search';
import { useDnsAlerts } from '../../dns-queries/hooks/useDnsAlerts';
import { useDomainWhois } from '../../dns-queries/hooks/useDomainWhois';
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

function lookupDomainForAlert(alert: DnsAlert): string | null {
  return alert.root_domain || alert.domain;
}

function AlertRow({
  alert,
  onWhois,
}: {
  alert: DnsAlert;
  onWhois: (alert: DnsAlert) => void;
}) {
  const label = TYPE_LABEL[alert.alert_type] || alert.alert_type;
  const severity = SEVERITY_COLOR[alert.severity] || 'default';
  const whoisDomain = lookupDomainForAlert(alert);
  const showReason = Boolean(alert.message);

  return (
    <ListItem
      sx={{ py: 0.75, px: 1.5 }}
      secondaryAction={
        whoisDomain ? (
          <Tooltip title={`WHOIS lookup: ${whoisDomain}`}>
            <IconButton edge="end" size="small" aria-label="WHOIS lookup" onClick={() => onWhois(alert)}>
              <SearchIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        ) : undefined
      }
    >
      <ListItemText
        primary={
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" sx={{ pr: whoisDomain ? 4 : 0 }}>
            <Chip label={label} size="small" color={severity} variant="outlined" />
            <Typography variant="body2" sx={{ fontWeight: 600, flex: 1 }}>
              {alert.domain || alert.root_domain || alert.message || 'Alert'}
            </Typography>
          </Stack>
        }
        secondary={
          <Stack spacing={0.75} sx={{ mt: 0.5 }}>
            <Stack direction="row" spacing={1.5} alignItems="center" flexWrap="wrap">
              <Typography variant="caption" color="text.secondary">
                {formatShortDateTime(alert.timestamp)}
              </Typography>
              {alert.client_ip && (
                <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                  {alert.client_ip}
                </Typography>
              )}
            </Stack>
            {showReason && (
              <Typography
                variant="caption"
                color={alert.alert_type === 'suspicious_domain' ? 'warning.main' : 'text.secondary'}
                sx={{ display: 'block', fontWeight: alert.alert_type === 'suspicious_domain' ? 600 : 400 }}
              >
                {alert.alert_type === 'suspicious_domain' ? 'Why suspicious: ' : ''}
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
  const { lookup, loading: whoisLoading, error: whoisError, result: whoisResult, reset: resetWhois } =
    useDomainWhois();
  const [whoisOpen, setWhoisOpen] = useState(false);
  const [whoisAlert, setWhoisAlert] = useState<DnsAlert | null>(null);

  const handleWhois = async (alert: DnsAlert) => {
    const domain = lookupDomainForAlert(alert);
    if (!domain) return;
    setWhoisAlert(alert);
    setWhoisOpen(true);
    resetWhois();
    await lookup(domain);
  };

  const handleCloseWhois = () => {
    setWhoisOpen(false);
    setWhoisAlert(null);
    resetWhois();
  };

  return (
    <>
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
                  <AlertRow alert={alert} onWhois={handleWhois} />
                  {index < items.length - 1 && <Divider component="li" />}
                </Box>
              ))}
            </List>
          )}
        </Box>
      </Paper>

      <Dialog open={whoisOpen} onClose={handleCloseWhois} maxWidth="md" fullWidth>
        <DialogTitle>
          WHOIS lookup
          {whoisAlert && lookupDomainForAlert(whoisAlert) ? ` — ${lookupDomainForAlert(whoisAlert)}` : ''}
        </DialogTitle>
        <DialogContent dividers>
          {whoisLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
              <CircularProgress size={28} />
            </Box>
          )}
          {!whoisLoading && whoisError && <Alert severity="error">{whoisError}</Alert>}
          {!whoisLoading && whoisResult && (
            <Stack spacing={1}>
              <Chip label={`Source: ${whoisResult.source}`} size="small" variant="outlined" />
              <Box
                component="pre"
                sx={{
                  m: 0,
                  p: 1.5,
                  bgcolor: 'action.hover',
                  borderRadius: 1,
                  overflow: 'auto',
                  maxHeight: 420,
                  fontFamily: 'monospace',
                  fontSize: '0.8rem',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {whoisResult.text}
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          {whoisAlert && lookupDomainForAlert(whoisAlert) && (
            <Button
              onClick={() => whoisAlert && handleWhois(whoisAlert)}
              disabled={whoisLoading}
            >
              Refresh
            </Button>
          )}
          <Button onClick={handleCloseWhois}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
