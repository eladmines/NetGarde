import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Copyright from '../internals/components/Copyright';
import CustomizedDataGrid from './CustomizedDataGrid';
import DnsLiveFeed from './DnsLiveFeed';
import LiveClientsView from './LiveClientsView';
import LiveNetworkGraph from './LiveNetworkGraph';
import BlockedClientsView from './BlockedClientsView';
import BlockedAttemptsView from './BlockedAttemptsView';
import DnsAlertsView from './DnsAlertsView';
import { useLiveClients } from '../hooks/useLiveClients';

export default function MainGrid() {
  const live = useLiveClients();

  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Overview
      </Typography>

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
          <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
            Live Clients
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

      <Grid container spacing={2} columns={12} sx={{ mt: 4 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <BlockedClientsView />
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <DnsAlertsView />
        </Grid>
      </Grid>

      <Grid container spacing={2} columns={12} sx={{ mt: 2 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <BlockedAttemptsView />
        </Grid>
      </Grid>

      <Typography component="h2" variant="h6" sx={{ mb: 2, mt: 4 }}>
        Blocked & Persisted Queries
      </Typography>
      <Grid container spacing={2} columns={12}>
        <Grid size={{ xs: 12 }}>
          <CustomizedDataGrid />
        </Grid>
      </Grid>
      <Copyright sx={{ my: 4 }} />
    </Box>
  );
}
