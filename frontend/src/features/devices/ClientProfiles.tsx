import { useState } from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import { useDevices } from './hooks/useDevices';
import ClientProfileDetail from './components/ClientProfileDetail';

export default function ClientProfiles() {
  const { devices, loading, error, refresh } = useDevices();
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const selected =
    devices.find((d) => d.id === selectedId) ?? (devices.length > 0 ? devices[0] : null);

  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
      <Typography component="h1" variant="h5" sx={{ mb: 0.5 }}>
        Client profiles
      </Typography>
      <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={1} sx={{ mb: 3 }}>
        <Typography variant="body2" color="text.secondary">
          Per-device DNS behavior baselines, scores, and policy controls.
        </Typography>
        <Button size="small" onClick={refresh} disabled={loading}>
          Refresh list
        </Button>
      </Stack>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      )}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {!loading && devices.length === 0 && (
        <Alert severity="info" variant="outlined">
          No clients registered yet. Devices appear after DHCP sync or when DNS traffic is observed
          from a known lease.
        </Alert>
      )}

      {!loading && devices.length > 0 && selected && (
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 4, lg: 3 }}>
            <Paper variant="outlined" sx={{ maxHeight: 560, overflow: 'auto' }}>
              <List dense disablePadding>
                {devices.map((d) => {
                  const isSelected = d.id === selected.id;
                  return (
                    <ListItemButton
                      key={d.id}
                      selected={isSelected}
                      onClick={() => setSelectedId(d.id)}
                    >
                      <ListItemText
                        primary={d.hostname || d.client_ip}
                        secondary={d.mac_address || d.client_ip}
                        primaryTypographyProps={{ fontWeight: isSelected ? 600 : 400 }}
                      />
                    </ListItemButton>
                  );
                })}
              </List>
            </Paper>
          </Grid>
          <Grid size={{ xs: 12, md: 8, lg: 9 }}>
            <ClientProfileDetail key={selected.id} device={selected} />
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
