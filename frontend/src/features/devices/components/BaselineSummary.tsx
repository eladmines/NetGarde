import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import IconButton from '@mui/material/IconButton';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import Stack from '@mui/material/Stack';

interface BaselineSummaryProps {
  baseline: Record<string, unknown>;
}

const METRIC_HELP: Record<string, string> = {
  median_queries_per_hour:
    'Typical DNS lookups per hour for this device (middle of recent history). Scoring compares the last 15 minutes to this “normal” level.',
  p95_queries_per_hour:
    'A busy-but-still-normal hour: 95% of past hours had fewer lookups than this. Spikes well above this can raise the behavior score.',
  mad_queries_per_hour:
    'How much hourly DNS volume usually swings above or below the median. A larger spread means habits are less predictable.',
  p95_new_roots_per_hour:
    'How many completely new websites (root domains) per hour are unusual but still typical. Many new sites in a short window can trigger an alert.',
  avg_new_roots_per_hour:
    'Average new sites per hour while the baseline was built. Helps describe how often this device discovers new domains.',
  total_queries:
    'Total DNS lookups counted across the baseline lookback window (about the last 7 days on the server).',
  rollup_hours:
    'Number of hourly buckets with data used to compute the baseline. More hours means a more reliable profile.',
};

function LabelWithHelp({ label, helpKey }: { label: string; helpKey: string }) {
  const help = METRIC_HELP[helpKey];
  return (
    <Stack direction="row" alignItems="center" spacing={0.25} component="span">
      <Typography variant="caption" color="text.secondary" component="span">
        {label}
      </Typography>
      {help && (
        <Tooltip title={help} arrow placement="top">
          <IconButton
            size="small"
            aria-label={`About ${label}`}
            sx={{ p: 0.25, color: 'text.secondary' }}
            tabIndex={0}
          >
            <HelpOutlineIcon sx={{ fontSize: 14 }} />
          </IconButton>
        </Tooltip>
      )}
    </Stack>
  );
}

function MetricCard({
  label,
  helpKey,
  value,
}: {
  label: string;
  helpKey: string;
  value: string;
}) {
  return (
    <Paper variant="outlined" sx={{ p: 1.5, height: '100%' }}>
      <LabelWithHelp label={label} helpKey={helpKey} />
      <Typography variant="h6" component="p" sx={{ mt: 0.5 }}>
        {value}
      </Typography>
    </Paper>
  );
}

function formatNum(value: unknown, digits = 1): string {
  if (value == null || value === '') return '—';
  const n = Number(value);
  if (Number.isNaN(n)) return String(value);
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

const BASELINE_METRICS: { label: string; helpKey: string; field: string; digits?: number }[] = [
  { label: 'Median queries / hour', helpKey: 'median_queries_per_hour', field: 'median_queries_per_hour' },
  { label: 'P95 queries / hour', helpKey: 'p95_queries_per_hour', field: 'p95_queries_per_hour' },
  { label: 'Typical spread (MAD)', helpKey: 'mad_queries_per_hour', field: 'mad_queries_per_hour' },
  { label: 'P95 new roots / hour', helpKey: 'p95_new_roots_per_hour', field: 'p95_new_roots_per_hour' },
  { label: 'Avg new roots / hour', helpKey: 'avg_new_roots_per_hour', field: 'avg_new_roots_per_hour' },
  { label: 'Total queries (window)', helpKey: 'total_queries', field: 'total_queries', digits: 0 },
  { label: 'Hours in baseline', helpKey: 'rollup_hours', field: 'rollup_hours', digits: 0 },
];

export default function BaselineSummary({ baseline }: BaselineSummaryProps) {
  const hourHist = baseline.hour_histogram as Record<string, number> | undefined;
  const topHours = hourHist
    ? Object.entries(hourHist)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([h, count]) => `${h}:00 UTC (${count})`)
        .join(', ')
    : null;

  return (
    <Box>
      <Grid container spacing={2}>
        {BASELINE_METRICS.map(({ label, helpKey, field, digits }) => (
          <Grid key={field} size={{ xs: 12, sm: 6, md: 4 }}>
            <MetricCard
              label={label}
              helpKey={helpKey}
              value={formatNum(baseline[field], digits ?? 1)}
            />
          </Grid>
        ))}
      </Grid>
      {topHours && (
        <Stack direction="row" alignItems="flex-start" spacing={0.25} sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary" component="span">
            Busiest hours: {topHours}
          </Typography>
          <Tooltip
            title="UTC hours when this device made the most DNS lookups while the baseline was built."
            arrow
            placement="top"
          >
            <IconButton
              size="small"
              aria-label="About busiest hours"
              sx={{ p: 0.25, color: 'text.secondary', mt: -0.25 }}
            >
              <HelpOutlineIcon sx={{ fontSize: 14 }} />
            </IconButton>
          </Tooltip>
        </Stack>
      )}
      {baseline.computed_at && (
        <Stack direction="row" alignItems="center" spacing={0.25} sx={{ mt: 1 }}>
          <Typography variant="caption" color="text.secondary" component="span">
            Baseline computed: {String(baseline.computed_at)}
          </Typography>
          <Tooltip
            title="When these stats were last recalculated from DNS history. The server refreshes them periodically while traffic flows."
            arrow
            placement="top"
          >
            <IconButton
              size="small"
              aria-label="About baseline computed time"
              sx={{ p: 0.25, color: 'text.secondary' }}
            >
              <HelpOutlineIcon sx={{ fontSize: 14 }} />
            </IconButton>
          </Tooltip>
        </Stack>
      )}
    </Box>
  );
}
