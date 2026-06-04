import { lazy, Suspense } from 'react';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import Copyright from '../internals/components/Copyright';
import DnsLiveFeed from './DnsLiveFeed';
import LiveClientsView from './LiveClientsView';
import LiveNetworkGraph from './LiveNetworkGraph';
import BlockedAttemptsView from './BlockedAttemptsView';
import DnsAlertsView from './DnsAlertsView';
import NetworkOverviewCard from './NetworkOverviewCard';
import { useLiveClients } from '../hooks/useLiveClients';

const ClientWorldMap = lazy(() => import('./ClientWorldMap'));

export default function MainGrid() {
  const live = useLiveClients();

  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Overview
      </Typography>

      <NetworkOverviewCard />

      <Grid container spacing={2} columns={12} sx={{ mb: 2 }}>
        <Grid size={{ xs: 12 }}>
          <Suspense
            fallback={
              <Paper variant="outlined" sx={{ p: 4, display: 'flex', justifyContent: 'center' }}>
                <CircularProgress size={28} />
              </Paper>
            }
          >
            <ClientWorldMap clients={live.clients} loading={live.loading} />
          </Suspense>
        </Grid>
      </Grid>

      <Grid container spacing={2} columns={12} sx={{ mb: 2 }}>
        <Grid size={{ xs: 12 }}>
          <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
            Live network
          </Typography>
          <Paper variant="outlined">
            <LiveNetworkGraph
              serverThroughput={live.serverThroughput}
              history={live.throughputHistory}
              usageError={live.usageError}
              onRefresh={live.refetch}
              refreshing={live.loading}
            />
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={2} columns={12}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Typography component="h2" variant="h6" sx={{ mb: 0.5 }}>
            Live Clients
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
            Connected clients and VPN login countries (GeoIP at enroll).
          </Typography>
          <LiveClientsView live={live} />
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
            Live DNS Feed
          </Typography>
          <DnsLiveFeed />
        </Grid>
      </Grid>

      <Grid container spacing={2} columns={12} sx={{ mt: 4, alignItems: 'stretch' }}>
        <Grid size={{ xs: 12, md: 6 }} sx={{ display: 'flex' }}>
          <Box sx={{ width: '100%' }}>
            <DnsAlertsView />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }} sx={{ display: 'flex' }}>
          <Box sx={{ width: '100%' }}>
            <BlockedAttemptsView />
          </Box>
        </Grid>
      </Grid>

      <Copyright sx={{ my: 4 }} />
    </Box>
  );
}
