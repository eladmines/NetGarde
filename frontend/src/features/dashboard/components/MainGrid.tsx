import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Copyright from '../internals/components/Copyright';
import CustomizedDataGrid from './CustomizedDataGrid';
import DnsStatsCards from './DnsStatsCards';
import DnsLiveFeed from './DnsLiveFeed';
import LiveClientsView from './LiveClientsView';
import BlockedAttemptsView from './BlockedAttemptsView';
import DnsAlertsView from './DnsAlertsView';
import { Link as RouterLink } from 'react-router-dom';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';

export default function MainGrid() {
  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Overview
      </Typography>
      <DnsStatsCards />
      <Paper variant="outlined" sx={{ p: 2, mt: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 1 }}>
        <Box>
          <Typography variant="subtitle1">Client behavior profiles</Typography>
          <Typography variant="body2" color="text.secondary">
            View baselines, scores, and per-device policy on the dedicated profiles page.
          </Typography>
        </Box>
        <Button component={RouterLink} to="/client-profiles" variant="outlined" size="small">
          Open client profiles
        </Button>
      </Paper>
      <Grid container spacing={2} columns={12} sx={{ mt: 2 }}>
        <Grid size={{ xs: 12 }}>
          <DnsAlertsView />
        </Grid>
      </Grid>
      <Grid container spacing={2} columns={12} sx={{ mt: 4 }}>
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
        <Grid size={{ xs: 12 }}>
          <Typography component="h2" variant="h6" sx={{ mb: 2, mt: 2 }}>
            Blocked Attempts
          </Typography>
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
