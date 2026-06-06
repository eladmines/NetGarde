import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Divider from '@mui/material/Divider';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import DevicesIcon from '@mui/icons-material/Devices';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import { Link as RouterLink } from 'react-router-dom';
import { useTheme } from '@mui/material/styles';
import { LiveClientRow, formatClientSource } from '../hooks/useLiveClients';
import { countryFlagEmoji, countryLabel } from '../../devices/utils/countryDisplay';
import { clientProfilePath } from '../../devices/clientProfilePaths';
import { formatBytesCompact, formatMibPerSec } from '../utils/formatBandwidth';
import { downloadChipSx, uploadChipSx } from '../utils/bandwidthColors';

export type CountryClientsSelection = {
  countryCode: string;
  countryName: string | null;
  clients: LiveClientRow[];
};

interface CountryClientsDialogProps {
  selection: CountryClientsSelection | null;
  onClose: () => void;
}

function ClientBandwidthChips({ client }: { client: LiveClientRow }) {
  const theme = useTheme();
  const bw = client.bandwidth;
  if (!bw) {
    return null;
  }
  return (
    <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
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
    </Stack>
  );
}

export default function CountryClientsDialog({ selection, onClose }: CountryClientsDialogProps) {
  const open = selection != null;
  const clients = selection?.clients ?? [];
  const sorted = [...clients].sort((a, b) => {
    const an = (a.hostname || a.client_ip).toLowerCase();
    const bn = (b.hostname || b.client_ip).toLowerCase();
    return an.localeCompare(bn);
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      {selection && (
        <>
          <DialogTitle sx={{ pb: 1 }}>
            <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
              <Typography component="span" sx={{ fontSize: '1.5rem', lineHeight: 1 }}>
                {countryFlagEmoji(selection.countryCode)}
              </Typography>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="h6" component="span">
                  {countryLabel(selection.countryCode, selection.countryName)}
                </Typography>
                <Typography variant="body2" color="text.secondary" display="block">
                  {clients.length} client{clients.length === 1 ? '' : 's'} · VPN login location
                </Typography>
              </Box>
            </Stack>
          </DialogTitle>
          <DialogContent dividers sx={{ p: 0 }}>
            <List disablePadding dense>
              {sorted.map((client, index) => {
                const title = client.hostname || client.client_ip;
                const subtitle = [
                  client.client_ip,
                  client.mac_address,
                  client.source ? formatClientSource(client.source) : null,
                ]
                  .filter(Boolean)
                  .join(' · ');

                const row = (
                  <>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      {client.source === 'vpn_enroll' ? (
                        <VpnKeyIcon color="primary" fontSize="small" />
                      ) : (
                        <DevicesIcon color="action" fontSize="small" />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Stack direction="row" spacing={0.75} alignItems="center" flexWrap="wrap" useFlexGap>
                          <Typography variant="body1" fontWeight={600}>
                            {title}
                          </Typography>
                          {client.is_active_now && (
                            <Chip
                              icon={<FiberManualRecordIcon sx={{ fontSize: '10px !important' }} />}
                              label="Active"
                              size="small"
                              color="success"
                              variant="outlined"
                              sx={{ height: 22 }}
                            />
                          )}
                        </Stack>
                      }
                      secondary={
                        <Stack spacing={0.75} sx={{ mt: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            {subtitle}
                          </Typography>
                          <ClientBandwidthChips client={client} />
                          {client.bandwidth && (
                            <Typography variant="caption" color="text.secondary">
                              +{formatBytesCompact(client.bandwidth.delta_rx_bytes)} ↓ / +
                              {formatBytesCompact(client.bandwidth.delta_tx_bytes)} ↑ last interval
                            </Typography>
                          )}
                          {!client.bandwidth && client.source === 'vpn_enroll' && (
                            <Typography variant="caption" color="text.secondary">
                              No live usage yet
                            </Typography>
                          )}
                        </Stack>
                      }
                    />
                  </>
                );

                if (client.device_id != null) {
                  return (
                    <Box key={client.device_id}>
                      {index > 0 && <Divider />}
                      <ListItemButton
                        component={RouterLink}
                        to={clientProfilePath(client.device_id)}
                        onClick={onClose}
                      >
                        {row}
                      </ListItemButton>
                    </Box>
                  );
                }

                return (
                  <Box key={client.client_ip}>
                    {index > 0 && <Divider />}
                    <Box sx={{ py: 1.5, px: 2, display: 'flex', alignItems: 'flex-start' }}>{row}</Box>
                  </Box>
                );
              })}
            </List>
          </DialogContent>
          <DialogActions>
            <Button onClick={onClose}>Close</Button>
          </DialogActions>
        </>
      )}
    </Dialog>
  );
}
