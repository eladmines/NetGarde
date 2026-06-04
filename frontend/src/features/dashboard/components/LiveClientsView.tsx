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
import PublicIcon from '@mui/icons-material/Public';
import {
  formatClientSource,
  LiveClientRow,
  LiveCountryItem,
  UseLiveClientsResult,
} from '../hooks/useLiveClients';
import { countryFlagEmoji, countryLabel } from '../../devices/utils/countryDisplay';
import { formatBytesCompact, formatMibPerSec } from '../utils/formatBandwidth';
import {
  downloadChipSx,
  downloadProgressSx,
  getBandwidthColors,
  uploadChipSx,
  uploadProgressSx,
} from '../utils/bandwidthColors';
import { useTheme } from '@mui/material/styles';

/** Live ↓/↑ rates from usage API — always shown when a sample exists (including 0 MiB/s). */
function ClientBandwidthRates({ client }: { client: LiveClientRow }) {
  const theme = useTheme();
  const bw = client.bandwidth;
  if (!bw) {
    return null;
  }
  return (
    <>
      <Chip
        size="small"
        variant="outlined"
        icon={<ArrowDownwardIcon sx={{ fontSize: '14px !important' }} />}
        label={`↓ ${formatMibPerSec(bw.rx_mib_per_sec)} MiB/s`}
        sx={{ height: 22, ...downloadChipSx(theme) }}
      />
      <Chip
        size="small"
        variant="outlined"
        icon={<ArrowUpwardIcon sx={{ fontSize: '14px !important' }} />}
        label={`↑ ${formatMibPerSec(bw.tx_mib_per_sec)} MiB/s`}
        sx={{ height: 22, ...uploadChipSx(theme) }}
      />
    </>
  );
}

function BandwidthDetail({ client }: { client: LiveClientRow }) {
  const theme = useTheme();
  const colors = getBandwidthColors(theme);
  const bw = client.bandwidth;

  if (!bw) {
    if (client.source === 'vpn_enroll') {
      return (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
          Waiting for usage — run netgarde-wg with{' '}
          <Typography component="span" variant="caption" sx={{ fontFamily: 'monospace' }}>
            --stats-interval 5
          </Typography>
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
      <Typography variant="caption" color="text.secondary">
        +{formatBytesCompact(bw.delta_rx_bytes)} ↓ / +{formatBytesCompact(bw.delta_tx_bytes)} ↑ in last
        reporting interval
      </Typography>
      <Stack direction="row" spacing={1} alignItems="center">
        <Typography variant="caption" sx={{ minWidth: 28, color: colors.download, fontWeight: 600 }}>
          ↓
        </Typography>
        <LinearProgress
          variant="determinate"
          value={downPct}
          sx={{ flex: 1, ...downloadProgressSx(theme) }}
        />
        <Typography variant="caption" sx={{ minWidth: 28, color: colors.upload, fontWeight: 600 }}>
          ↑
        </Typography>
        <LinearProgress
          variant="determinate"
          value={upPct}
          sx={{ flex: 1, ...uploadProgressSx(theme) }}
        />
      </Stack>
    </Stack>
  );
}

function LiveCountriesList({ countries }: { countries: LiveCountryItem[] }) {
  if (countries.length === 0) {
    return null;
  }
  return (
    <Box sx={{ px: 2, py: 1.25, borderBottom: 1, borderColor: 'divider', bgcolor: 'action.hover' }}>
      <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mb: 0.75 }}>
        <PublicIcon sx={{ fontSize: 16 }} color="primary" />
        <Typography variant="caption" fontWeight={600} color="text.secondary">
          Live countries (VPN login)
        </Typography>
      </Stack>
      <Stack direction="row" flexWrap="wrap" gap={0.75} useFlexGap>
        {countries.map((c) => (
          <Chip
            key={c.country_code}
            size="small"
            variant="outlined"
            label={`${c.country_name || c.country_code} (${c.client_count})`}
            icon={
              c.country_code !== 'UNKNOWN' ? (
                <span aria-hidden>{countryFlagEmoji(c.country_code)}</span>
              ) : undefined
            }
          />
        ))}
      </Stack>
    </Box>
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
            {client.vpn_login_country_code && (
              <Tooltip
                title={countryLabel(
                  client.vpn_login_country_code,
                  client.vpn_login_country_name,
                )}
                arrow
              >
                <Typography
                  component="span"
                  aria-label={countryLabel(
                    client.vpn_login_country_code,
                    client.vpn_login_country_name,
                  )}
                  sx={{ fontSize: '1.25rem', lineHeight: 1 }}
                >
                  {countryFlagEmoji(client.vpn_login_country_code)}
                </Typography>
              </Tooltip>
            )}
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
            <ClientBandwidthRates client={client} />
          </Stack>
        }
        secondary={
          <Box component="span" sx={{ display: 'block' }}>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.25, display: 'block' }}>
              {subtitleParts.join(' · ')}
            </Typography>
            {client.vpn_login_country_code && (
              <Typography variant="caption" color="text.secondary" display="block">
                Last VPN login from:{' '}
                {countryLabel(
                  client.vpn_login_country_code,
                  client.vpn_login_country_name,
                )}
              </Typography>
            )}
            <BandwidthDetail client={client} />
          </Box>
        }
      />
    </ListItemButton>
  );
}

export interface LiveClientsViewProps {
  live: UseLiveClientsResult;
}

export default function LiveClientsView({ live }: LiveClientsViewProps) {
  const {
    clients,
    liveCountries,
    loading,
    error,
    usageError,
    enrolledCount,
    serverThroughput,
    refetch,
  } = live;

  if (loading && clients.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper variant="outlined" sx={{ maxHeight: 500, display: 'flex', flexDirection: 'column' }}>
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

      {usageError && (
        <Alert severity="info" sx={{ mx: 2, mt: 1 }}>
          Bandwidth: {usageError}
        </Alert>
      )}

      {clients.length > 0 && <LiveCountriesList countries={liveCountries} />}

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
