import { lazy, Suspense } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useLiveClients } from '../features/dashboard/hooks/useLiveClients';

const ClientWorldMap = lazy(() => import('../features/dashboard/components/ClientWorldMap'));

export default function ClientMapPage() {
  const live = useLiveClients();

  return (
    <Box sx={{ maxWidth: 1200 }}>
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        justifyContent="space-between"
        alignItems={{ xs: 'stretch', sm: 'flex-start' }}
        spacing={1}
        sx={{ mb: 2 }}
      >
        <Box>
          <Typography component="h1" variant="h5" sx={{ mb: 0.5, fontWeight: 600 }}>
            Client map
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Where your clients last connected to VPN (GeoIP from public IP at enroll). Click a
            country flag to see all clients there. Not DNS domain country.
          </Typography>
        </Box>
        <Button
          size="small"
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={live.refetch}
          disabled={live.loading}
          sx={{ flexShrink: 0, alignSelf: { sm: 'flex-start' } }}
        >
          Refresh
        </Button>
      </Stack>

      <Suspense
        fallback={
          <Paper variant="outlined" sx={{ p: 6, display: 'flex', justifyContent: 'center' }}>
            <CircularProgress size={32} />
          </Paper>
        }
      >
        <ClientWorldMap clients={live.clients} loading={live.loading} showHeader={false} />
      </Suspense>
    </Box>
  );
}
