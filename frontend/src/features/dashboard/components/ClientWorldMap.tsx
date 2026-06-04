import { useMemo } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import { useNavigate } from 'react-router-dom';
import { useTheme, alpha } from '@mui/material/styles';
import worldMap from '@svg-maps/world';
import PublicIcon from '@mui/icons-material/Public';
import { LiveClientRow } from '../hooks/useLiveClients';
import { countryFlagEmoji, countryLabel } from '../../devices/utils/countryDisplay';
import { countryCodeToMapPoint, WORLD_MAP_VIEW_BOX } from '../utils/countryCentroids';
import { clientProfilePath } from '../../devices/clientProfilePaths';

const MAP_VIEW_BOX = worldMap.viewBox || WORLD_MAP_VIEW_BOX;
const JITTER_RADIUS = 18;

type MapMarker = {
  key: string;
  x: number;
  y: number;
  flag: string;
  label: string;
  tooltip: string;
  active: boolean;
  deviceId: number | null;
};

function jitterPosition(
  base: { x: number; y: number },
  index: number,
  total: number,
): { x: number; y: number } {
  if (total <= 1) {
    return base;
  }
  const angle = (2 * Math.PI * index) / total;
  return {
    x: base.x + JITTER_RADIUS * Math.cos(angle),
    y: base.y + JITTER_RADIUS * Math.sin(angle),
  };
}

function buildMarkers(clients: LiveClientRow[]): MapMarker[] {
  const withCountry = clients.filter((c) => c.vpn_login_country_code);
  const byCountry = new Map<string, LiveClientRow[]>();
  for (const c of withCountry) {
    const code = c.vpn_login_country_code!.toUpperCase();
    const list = byCountry.get(code) ?? [];
    list.push(c);
    byCountry.set(code, list);
  }

  const markers: MapMarker[] = [];
  for (const [code, group] of byCountry.entries()) {
    const base = countryCodeToMapPoint(code);
    if (!base) {
      continue;
    }
    group.forEach((client, index) => {
      const pos = jitterPosition(base, index, group.length);
      const name = client.hostname || client.client_ip;
      const countryName = client.vpn_login_country_name;
      markers.push({
        key: `${code}-${client.device_id ?? client.client_ip}-${index}`,
        x: pos.x,
        y: pos.y,
        flag: countryFlagEmoji(code),
        label: countryLabel(code, countryName),
        tooltip: `${name} · ${countryLabel(code, countryName)}${client.is_active_now ? ' · Active' : ''}`,
        active: client.is_active_now,
        deviceId: client.device_id,
      });
    });
  }
  return markers;
}

interface ClientWorldMapProps {
  clients: LiveClientRow[];
  loading?: boolean;
}

export default function ClientWorldMap({ clients, loading = false }: ClientWorldMapProps) {
  const theme = useTheme();
  const navigate = useNavigate();

  const markers = useMemo(() => buildMarkers(clients), [clients]);

  const highlightedCountryIds = useMemo(() => {
    const ids = new Set<string>();
    for (const c of clients) {
      const code = c.vpn_login_country_code?.trim().toLowerCase();
      if (code && code !== 'unknown' && code !== 'global') {
        ids.add(code);
      }
    }
    return ids;
  }, [clients]);

  const unknownCount = clients.filter((c) => !c.vpn_login_country_code).length;
  const placedCount = markers.length;

  const landFill = alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.12 : 0.08);
  const landHighlight = alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.38 : 0.28);
  const landStroke = alpha(theme.palette.divider, 0.9);
  const oceanFill =
    theme.palette.mode === 'dark'
      ? alpha(theme.palette.background.default, 0.6)
      : alpha(theme.palette.primary.main, 0.04);

  return (
    <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
        <PublicIcon color="primary" fontSize="small" />
        <Typography variant="subtitle1" fontWeight={600} sx={{ flex: 1 }}>
          Clients on the map
        </Typography>
        <Chip
          size="small"
          variant="outlined"
          label={`${placedCount} located`}
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
        VPN login country (GeoIP at enroll). Hover a flag for the client; green ring = active now.
      </Typography>

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
          {markers.map((m) => (
            <g
              key={m.key}
              transform={`translate(${m.x}, ${m.y})`}
              style={{ cursor: m.deviceId != null ? 'pointer' : 'default' }}
              onClick={() => {
                if (m.deviceId != null) {
                  navigate(clientProfilePath(m.deviceId));
                }
              }}
              role={m.deviceId != null ? 'button' : undefined}
              tabIndex={m.deviceId != null ? 0 : undefined}
              onKeyDown={(e) => {
                if (m.deviceId != null && (e.key === 'Enter' || e.key === ' ')) {
                  e.preventDefault();
                  navigate(clientProfilePath(m.deviceId));
                }
              }}
            >
              <title>{m.tooltip}</title>
              <circle
                r={16}
                fill={theme.palette.background.paper}
                stroke={m.active ? theme.palette.success.main : theme.palette.primary.main}
                strokeWidth={m.active ? 2.5 : 1.5}
              />
              <text
                textAnchor="middle"
                dominantBaseline="central"
                fontSize={15}
                style={{ pointerEvents: 'none' }}
              >
                {m.flag}
              </text>
            </g>
          ))}
        </Box>
      </Box>

      {!loading && clients.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
          No clients yet. Devices appear after VPN enroll or DHCP sync.
        </Typography>
      )}
      {!loading && clients.length > 0 && placedCount === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
          No VPN login location recorded yet. Re-enroll with netgarde-wg to populate the map.
        </Typography>
      )}
    </Paper>
  );
}
