import { useCallback, useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import LinearProgress from '@mui/material/LinearProgress';
import Tooltip from '@mui/material/Tooltip';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import PublicIcon from '@mui/icons-material/Public';
import { devicesApi } from '../config/api';
import { DeviceCountryBreakdown } from '../types/device';
import { countryFlagEmoji, countryLabel } from '../utils/countryDisplay';

interface DeviceCountriesSectionProps {
  deviceId: number;
}

export default function DeviceCountriesSection({ deviceId }: DeviceCountriesSectionProps) {
  const [data, setData] = useState<DeviceCountryBreakdown | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const breakdown = await devicesApi.getDnsCountries(deviceId, 168);
      setData(breakdown);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load country breakdown');
    } finally {
      setLoading(false);
    }
  }, [deviceId]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <Box>
      <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mb: 1 }}>
        <PublicIcon color="primary" fontSize="small" />
        <Typography variant="subtitle1" sx={{ flex: 1 }}>
          DNS countries (last 7 days)
        </Typography>
        <Tooltip
          title="Estimated from domain endings (e.g. .il, .de, .co.uk). Global sites (.com) count as Global. Based on all DNS seen by NetGarde, not only blocked queries."
          arrow
        >
          <Box
            component="span"
            aria-label="About DNS countries"
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              cursor: 'help',
              color: 'text.secondary',
              '&:hover': { color: 'text.primary' },
            }}
          >
            <HelpOutlineIcon sx={{ fontSize: 18 }} />
          </Box>
        </Tooltip>
      </Stack>

      {loading && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CircularProgress size={20} />
          <Typography variant="body2" color="text.secondary">
            Loading…
          </Typography>
        </Box>
      )}
      {error && (
        <Alert severity="warning" sx={{ mb: 1 }}>
          {error}
        </Alert>
      )}
      {!loading && data && (
        <>
          {data.primary_country_code && (
            <Chip
              size="small"
              label={countryLabel(data.primary_country_code, data.primary_country_name)}
              variant="outlined"
              sx={{ mb: 1.5 }}
            />
          )}
          {data.note && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {data.note}
            </Typography>
          )}
          {data.countries.length === 0 ? null : (
            <Stack spacing={1.25}>
              {data.countries.map((c) => (
                <Box key={c.country_code}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Stack direction="row" alignItems="center" spacing={0.5}>
                      <Typography variant="body2">
                        {countryFlagEmoji(c.country_code)} {c.country_name}
                      </Typography>
                      {c.is_new && (
                        <Chip size="small" label="New" color="warning" variant="outlined" />
                      )}
                    </Stack>
                    <Typography variant="caption" color="text.secondary">
                      {c.share_percent}% · {c.query_count.toLocaleString()} queries
                    </Typography>
                  </Stack>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(100, c.share_percent)}
                    sx={{ mt: 0.5, height: 6, borderRadius: 1 }}
                  />
                </Box>
              ))}
            </Stack>
          )}
        </>
      )}
    </Box>
  );
}
