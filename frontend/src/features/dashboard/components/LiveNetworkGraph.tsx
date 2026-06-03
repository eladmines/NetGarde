import { useMemo } from 'react';
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Chip from '@mui/material/Chip';
import { LineChart } from '@mui/x-charts/LineChart';
import type { NetworkThroughputPoint, ServerNetworkThroughput } from '../types/networkThroughput';
import { formatMibPerSec } from '../utils/formatBandwidth';

function AreaGradient({ color, id }: { color: string; id: string }) {
  return (
    <defs>
      <linearGradient id={id} x1="50%" y1="0%" x2="50%" y2="100%">
        <stop offset="0%" stopColor={color} stopOpacity={0.45} />
        <stop offset="100%" stopColor={color} stopOpacity={0} />
      </linearGradient>
    </defs>
  );
}

interface LiveNetworkGraphProps {
  serverThroughput: ServerNetworkThroughput;
  history: NetworkThroughputPoint[];
  usageError: string | null;
}

export default function LiveNetworkGraph({
  serverThroughput,
  history,
  usageError,
}: LiveNetworkGraphProps) {
  const theme = useTheme();

  const peakTotal = useMemo(
    () => history.reduce((max, p) => Math.max(max, p.total_mib_per_sec), 0),
    [history],
  );

  const chartReady = history.length >= 2;
  const labels = history.map((p) => p.label);
  const downSeries = history.map((p) => p.rx_mib_per_sec);
  const upSeries = history.map((p) => p.tx_mib_per_sec);

  const downColor = theme.palette.info.main;
  const upColor = theme.palette.secondary.main;

  return (
    <Box sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: 'divider' }}>
      <Stack
        direction="row"
        alignItems="baseline"
        spacing={1}
        flexWrap="wrap"
        useFlexGap
        sx={{ mb: 1 }}
      >
        <Typography variant="subtitle2" component="span">
          Live network throughput
        </Typography>
        <Typography variant="caption" color="text.secondary">
          All VPN clients reporting to server
        </Typography>
      </Stack>

      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 1.5 }}>
        <Chip
          size="small"
          color="primary"
          variant="outlined"
          label={`Total ${formatMibPerSec(serverThroughput.total_mib_per_sec)} MiB/s`}
        />
        <Chip
          size="small"
          variant="outlined"
          label={`↓ ${formatMibPerSec(serverThroughput.rx_mib_per_sec)} MiB/s`}
        />
        <Chip
          size="small"
          variant="outlined"
          label={`↑ ${formatMibPerSec(serverThroughput.tx_mib_per_sec)} MiB/s`}
        />
        <Chip
          size="small"
          variant="outlined"
          label={`${serverThroughput.reporting_clients} reporting`}
        />
        {peakTotal > 0 && (
          <Chip size="small" variant="outlined" label={`Peak ${formatMibPerSec(peakTotal)} MiB/s`} />
        )}
      </Stack>

      {usageError ? (
        <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
          Graph unavailable: {usageError}
        </Typography>
      ) : !chartReady ? (
        <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
          Collecting samples… Run netgarde-wg with{' '}
          <Typography component="span" variant="body2" sx={{ fontFamily: 'monospace' }}>
            --stats-interval 5
          </Typography>{' '}
          so usage reaches the API.
        </Typography>
      ) : (
        <LineChart
          height={200}
          margin={{ left: 4, right: 12, top: 8, bottom: 0 }}
          grid={{ horizontal: true }}
          xAxis={[
            {
              scaleType: 'point',
              data: labels,
              tickInterval: (_value, index) => index === 0 || index === labels.length - 1,
            },
          ]}
          yAxis={[
            {
              width: 44,
              label: 'MiB/s',
            },
          ]}
          series={[
            {
              id: 'download',
              label: 'Download',
              data: downSeries,
              showMark: false,
              curve: 'linear',
              area: true,
              color: downColor,
            },
            {
              id: 'upload',
              label: 'Upload',
              data: upSeries,
              showMark: false,
              curve: 'linear',
              area: true,
              color: upColor,
            },
          ]}
          sx={{
            '& .MuiAreaElement-series-download': {
              fill: "url('#netgarde-down')",
            },
            '& .MuiAreaElement-series-upload': {
              fill: "url('#netgarde-up')",
            },
          }}
        >
          <AreaGradient color={downColor} id="netgarde-down" />
          <AreaGradient color={upColor} id="netgarde-up" />
        </LineChart>
      )}
    </Box>
  );
}
