import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import NetworkTopologyView from '../features/network/components/NetworkTopologyView';

export default function NetworkTopologyPage() {
  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1200px' } }}>
      <Typography component="h1" variant="h5" sx={{ mb: 2 }}>
        VPN network
      </Typography>
      <NetworkTopologyView />
    </Box>
  );
}
