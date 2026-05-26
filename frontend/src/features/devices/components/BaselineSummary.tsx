import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';

interface BaselineSummaryProps {
  baseline: Record<string, unknown>;
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <Paper variant="outlined" sx={{ p: 1.5, height: '100%' }}>
      <Typography variant="caption" color="text.secondary" display="block">
        {label}
      </Typography>
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
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <MetricCard label="Median queries / hour" value={formatNum(baseline.median_queries_per_hour)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <MetricCard label="P95 queries / hour" value={formatNum(baseline.p95_queries_per_hour)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <MetricCard label="Typical spread (MAD)" value={formatNum(baseline.mad_queries_per_hour)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <MetricCard label="P95 new roots / hour" value={formatNum(baseline.p95_new_roots_per_hour)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <MetricCard label="Avg new roots / hour" value={formatNum(baseline.avg_new_roots_per_hour)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <MetricCard label="Total queries (window)" value={formatNum(baseline.total_queries, 0)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <MetricCard label="Hours in baseline" value={formatNum(baseline.rollup_hours, 0)} />
        </Grid>
      </Grid>
      {topHours && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Busiest hours: {topHours}
        </Typography>
      )}
      {baseline.computed_at && (
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
          Baseline computed: {String(baseline.computed_at)}
        </Typography>
      )}
    </Box>
  );
}
