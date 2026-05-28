import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Copyright from '../internals/components/Copyright';
import CustomizedDataGrid from './CustomizedDataGrid';
import DnsLiveFeed from './DnsLiveFeed';
import LiveClientsView from './LiveClientsView';
import BlockedAttemptsView from './BlockedAttemptsView';
import DnsAlertsView from './DnsAlertsView';
import NetworkTopologyView from '../../network/components/NetworkTopologyView';

export default function MainGrid() {
  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Overview
      </Typography>

      <Box sx={{ mb: 3 }}>
        <NetworkTopologyView />
      </Box>

      <Grid container spacing={2} columns={12}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
            Live Clients
          </Typography>
          <LiveClientsView />
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
          <DnsAlertsView />
        </Grid>
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
