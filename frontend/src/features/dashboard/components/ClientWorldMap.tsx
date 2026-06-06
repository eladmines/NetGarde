import { useMemo, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import { useTheme, alpha } from '@mui/material/styles';
import worldMap from '@svg-maps/world';
import PublicIcon from '@mui/icons-material/Public';
import { LiveClientRow } from '../hooks/useLiveClients';
import { countryFlagEmoji, countryLabel } from '../../devices/utils/countryDisplay';
import { countryCodeToMapPoint, WORLD_MAP_VIEW_BOX } from '../utils/countryCentroids';
import CountryClientsDialog, { CountryClientsSelection } from './CountryClientsDialog';

const MAP_VIEW_BOX = worldMap.viewBox || WORLD_MAP_VIEW_BOX;

type CountryMarker = {
  countryCode: string;
  countryName: string | null;
  x: number;
  y: number;
  clients: LiveClientRow[];
  activeCount: number;
};

function buildCountryMarkers(clients: LiveClientRow[]): CountryMarker[] {
  const byCountry = new Map<string, LiveClientRow[]>();
  for (const c of clients) {
    const code = c.vpn_login_country_code?.trim().toUpperCase();
    if (!code || code === 'UNKNOWN' || code === 'GLOBAL') {
      continue;
    }
    const list = byCountry.get(code) ?? [];
    list.push(c);
    byCountry.set(code, list);
  }

  const markers: CountryMarker[] = [];
  for (const [countryCode, group] of byCountry.entries()) {
    const base = countryCodeToMapPoint(countryCode);
    if (!base) {
      continue;
    }
    markers.push({
      countryCode,
      countryName: group[0]?.vpn_login_country_name ?? null,
      x: base.x,
      y: base.y,
      clients: group,
      activeCount: group.filter((c) => c.is_active_now).length,
    });
  }
  return markers;
}

interface ClientWorldMapProps {
  clients: LiveClientRow[];
  loading?: boolean;
  /** When false, page supplies the title (e.g. Client map route). */
  showHeader?: boolean;
}

export default function ClientWorldMap({
  clients,
  loading = false,
  showHeader = true,
}: ClientWorldMapProps) {
  const theme = useTheme();
  const [selection, setSelection] = useState<CountryClientsSelection | null>(null);

  const countryMarkers = useMemo(() => buildCountryMarkers(clients), [clients]);

  const highlightedCountryIds = useMemo(() => {
    return new Set(countryMarkers.map((m) => m.countryCode.toLowerCase()));
  }, [countryMarkers]);

  const placedClientCount = countryMarkers.reduce((n, m) => n + m.clients.length, 0);
  const unknownCount = clients.filter((c) => !c.vpn_login_country_code).length;

  const landFill = alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.12 : 0.08);
  const landHighlight = alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.38 : 0.28);
  const landStroke = alpha(theme.palette.divider, 0.9);
  const oceanFill =
    theme.palette.mode === 'dark'
      ? alpha(theme.palette.background.default, 0.6)
      : alpha(theme.palette.primary.main, 0.04);

  const openCountryDialog = (marker: CountryMarker) => {
    setSelection({
      countryCode: marker.countryCode,
      countryName: marker.countryName,
      clients: marker.clients,
    });
  };

  return (
    <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
      {showHeader && (
        <>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
            <PublicIcon color="primary" fontSize="small" />
            <Typography variant="subtitle1" fontWeight={600} sx={{ flex: 1 }}>
              Client map
            </Typography>
            <Chip
              size="small"
              variant="outlined"
              label={`${placedClientCount} located`}
              sx={{ height: 24 }}
            />
            {unknownCount > 0 && (
              <Chip
                size="small"
                variant="outlined"
                label={`${unknownCount} no VPN geo`}
                sx={{ height: 24 }}
              />
            )}
          </Stack>
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1.5 }}>
            Click a flag to see all clients in that country. Green ring = at least one active now.
          </Typography>
        </>
      )}
      {!showHeader && (
        <Stack direction="row" flexWrap="wrap" gap={0.75} sx={{ mb: 1.5 }}>
          <Chip size="small" variant="outlined" label={`${placedClientCount} located`} />
          {unknownCount > 0 && (
            <Chip size="small" variant="outlined" label={`${unknownCount} no VPN geo`} />
          )}
          <Chip size="small" variant="outlined" label={`${clients.length} clients`} />
        </Stack>
      )}

      <Box
        sx={{
          position: 'relative',
          width: '100%',
          borderRadius: 1,
          overflow: 'hidden',
          bgcolor: oceanFill,
          border: `1px solid ${theme.palette.divider}`,
        }}
      >
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 2,
              bgcolor: alpha(theme.palette.background.paper, 0.55),
            }}
          >
            <CircularProgress size={28} />
          </Box>
        )}
        <Box
          component="svg"
          viewBox={MAP_VIEW_BOX}
          preserveAspectRatio="xMidYMid meet"
          sx={{ width: '100%', height: 'auto', display: 'block', minHeight: 220 }}
          role="img"
          aria-label="World map showing client VPN login countries"
        >
          {worldMap.locations.map((loc) => {
            const highlighted = highlightedCountryIds.has(loc.id);
            return (
              <path
                key={loc.id}
                d={loc.path}
                fill={highlighted ? landHighlight : landFill}
                stroke={landStroke}
                strokeWidth={0.5}
              />
            );
          })}
          {countryMarkers.map((m) => {
            const count = m.clients.length;
            const hasActive = m.activeCount > 0;
            const tooltip = `${countryLabel(m.countryCode, m.countryName)} · ${count} client${count === 1 ? '' : 's'}${hasActive ? ` · ${m.activeCount} active` : ''}`;
            return (
              <g
                key={m.countryCode}
                transform={`translate(${m.x}, ${m.y})`}
                style={{ cursor: 'pointer' }}
                onClick={() => openCountryDialog(m)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    openCountryDialog(m);
                  }
                }}
              >
                <title>{tooltip}</title>
                <circle
                  r={18}
                  fill={theme.palette.background.paper}
                  stroke={hasActive ? theme.palette.success.main : theme.palette.primary.main}
                  strokeWidth={hasActive ? 1.75 : 1.5}
                />
                <text
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize={16}
                  y={count > 1 ? -3 : 0}
                  style={{ pointerEvents: 'none' }}
                >
                  {countryFlagEmoji(m.countryCode)}
                </text>
                {count > 1 && (
                  <text
                    textAnchor="middle"
                    dominantBaseline="central"
                    fontSize={9}
                    fontWeight={700}
                    y={11}
                    fill={theme.palette.text.secondary}
                    style={{ pointerEvents: 'none' }}
                  >
                    {count}
                  </text>
                )}
              </g>
            );
          })}
        </Box>
      </Box>

      <CountryClientsDialog selection={selection} onClose={() => setSelection(null)} />

      {!loading && clients.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
          No clients yet. Devices appear after VPN enroll or DHCP sync.
        </Typography>
      )}
      {!loading && clients.length > 0 && countryMarkers.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
          No VPN login location recorded yet. Re-enroll with netgarde-wg to populate the map.
        </Typography>
      )}
    </Paper>
  );
}
