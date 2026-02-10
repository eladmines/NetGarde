import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import DnsIcon from '@mui/icons-material/Dns';
import BlockIcon from '@mui/icons-material/Block';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PercentIcon from '@mui/icons-material/Percent';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import { useDnsStats } from '../../dns-queries/hooks/useDnsStats';

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
}

export default function DnsStatsCards() {
  const { stats, loading } = useDnsStats();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!stats) {
    return (
      <Typography color="text.secondary" sx={{ py: 2 }}>
        Unable to load DNS statistics.
      </Typography>
    );
  }

  const statCards = [
    {
      title: 'Total Queries',
      value: formatNumber(stats.total_queries),
      icon: <DnsIcon sx={{ color: '#0078d4' }} />,
      color: '#0078d4',
    },
    {
      title: 'Blocked',
      value: formatNumber(stats.blocked_queries),
      icon: <BlockIcon sx={{ color: '#d32f2f' }} />,
      color: '#d32f2f',
    },
    {
      title: 'Allowed',
      value: formatNumber(stats.allowed_queries),
      icon: <CheckCircleIcon sx={{ color: '#2e7d32' }} />,
      color: '#2e7d32',
    },
    {
      title: 'Block Rate',
      value: stats.block_rate + '%',
      icon: <PercentIcon sx={{ color: '#ed6c02' }} />,
      color: '#ed6c02',
    },
  ];

  return (
    <Grid container spacing={2} columns={12} sx={{ mb: 2 }}>
      {statCards.map((card, index) => (
        <Grid key={index} size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined" sx={{ height: '100%' }}>
            <CardContent>
              <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  {card.title}
                </Typography>
                {card.icon}
              </Stack>
              <Typography variant="h4" component="p" sx={{ color: card.color, fontWeight: 600 }}>
                {card.value}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}

      {/* Top Blocked Domains */}
      {stats.top_blocked_domains.length > 0 && (
        <Grid size={{ xs: 12, md: 6 }}>
          <Card variant="outlined" sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                Top Blocked Domains
              </Typography>
              <List dense disablePadding>
                {stats.top_blocked_domains.slice(0, 5).map((item, index) => (
                  <ListItem key={index} disablePadding sx={{ py: 0.5 }}>
                    <ListItemText
                      primary={item.domain}
                      primaryTypographyProps={{ variant: 'body2', noWrap: true }}
                    />
                    <Chip label={item.count} size="small" color="error" variant="outlined" />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      )}

      {/* Top Clients */}
      {stats.top_clients.length > 0 && (
        <Grid size={{ xs: 12, md: 6 }}>
          <Card variant="outlined" sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                Top Clients
              </Typography>
              <List dense disablePadding>
                {stats.top_clients.slice(0, 5).map((item, index) => (
                  <ListItem key={index} disablePadding sx={{ py: 0.5 }}>
                    <ListItemText
                      primary={item.client_ip}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                    <Chip label={item.count + ' queries'} size="small" color="info" variant="outlined" />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );
}
