import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Chip from '@mui/material/Chip';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import RefreshIcon from '@mui/icons-material/Refresh';
import SummarizeOutlinedIcon from '@mui/icons-material/SummarizeOutlined';
import { useNetworkOverview } from '../hooks/useNetworkOverview';
import { formatShortDateTime } from '../../../shared/utils/dateUtils';

export default function NetworkOverviewCard() {
  const { data, loading, error, refetch } = useNetworkOverview(60);

  const stats = data?.stats;

  return (
    <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
        <SummarizeOutlinedIcon color="primary" fontSize="small" />
        <Typography component="h3" variant="subtitle1" sx={{ fontWeight: 600, flex: 1 }}>
          Network review
        </Typography>
        {data && (
          <Typography variant="caption" color="text.secondary">
            Last {data.period_minutes} min · {formatShortDateTime(data.generated_at)}
          </Typography>
        )}
        <Tooltip title="Refresh review">
          <span>
            <IconButton size="small" onClick={() => refetch()} disabled={loading} aria-label="Refresh network review">
              {loading ? <CircularProgress size={18} /> : <RefreshIcon fontSize="small" />}
            </IconButton>
          </span>
        </Tooltip>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 1.5 }}>
          {error}
        </Alert>
      )}

      {stats && (
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 1.5 }}>
          <Chip size="small" label={`${stats.reporting_clients} live`} variant="outlined" />
          <Chip size="small" label={`${stats.live_total_mib_per_sec.toFixed(1)} MiB/s now`} variant="outlined" />
          <Chip size="small" label={`Peak ${stats.peak_mib_per_sec.toFixed(1)} MiB/s`} variant="outlined" />
          <Chip
            size="small"
            label={`${stats.alerts_total} alerts`}
            color={stats.alerts_total > 0 ? 'warning' : 'default'}
            variant="outlined"
          />
          <Chip
            size="small"
            label={`${stats.blocked_queries} blocked`}
            color={stats.blocked_queries > 0 ? 'error' : 'default'}
            variant="outlined"
          />
          <Chip size="small" label={`${stats.enabled_policy_packs} packs`} variant="outlined" />
          {stats.elevated_behavior_clients > 0 && (
            <Chip
              size="small"
              label={`${stats.elevated_behavior_clients} behavior`}
              color="warning"
              variant="outlined"
            />
          )}
        </Stack>
      )}

      {loading && !data ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
          <CircularProgress size={28} />
        </Box>
      ) : (
        <List dense disablePadding>
          {(data?.bullets ?? []).map((bullet, index) => (
            <ListItem key={index} disableGutters sx={{ py: 0.25 }}>
              <ListItemIcon sx={{ minWidth: 28 }}>
                <FiberManualRecordIcon sx={{ fontSize: 8, color: 'text.secondary' }} />
              </ListItemIcon>
              <ListItemText
                primary={bullet}
                primaryTypographyProps={{ variant: 'body2', color: 'text.primary' }}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
}
