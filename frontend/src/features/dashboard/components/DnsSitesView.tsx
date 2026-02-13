import { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import Divider from '@mui/material/Divider';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import Collapse from '@mui/material/Collapse';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import CircularProgress from '@mui/material/CircularProgress';
import RefreshIcon from '@mui/icons-material/Refresh';
import LanguageIcon from '@mui/icons-material/Language';
import BlockIcon from '@mui/icons-material/Block';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import FilterAltOffIcon from '@mui/icons-material/FilterAltOff';
import { useDnsSites } from '../../dns-queries/hooks/useDnsSites';
import { DnsSiteGroup } from '../../dns-queries/types/dnsQuery';

function formatTime(timestamp: string | null): string {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

function SiteRow({ site }: { site: DnsSiteGroup }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <ListItem
        sx={{
          py: 1,
          px: 2,
          backgroundColor: site.blocked ? 'rgba(211, 47, 47, 0.06)' : 'transparent',
          '&:hover': {
            backgroundColor: site.blocked ? 'rgba(211, 47, 47, 0.1)' : 'action.hover',
          },
          cursor: site.subdomains.length > 1 ? 'pointer' : 'default',
        }}
        onClick={() => site.subdomains.length > 1 && setExpanded(!expanded)}
      >
        <ListItemIcon sx={{ minWidth: 36 }}>
          {site.blocked ? (
            <BlockIcon color="error" fontSize="small" />
          ) : (
            <LanguageIcon color="primary" fontSize="small" />
          )}
        </ListItemIcon>
        <ListItemText
          primary={
            <Stack direction="row" spacing={1.5} alignItems="center">
              <Typography variant="body1" sx={{ fontWeight: 600, flex: 1 }}>
                {site.root_domain}
              </Typography>
              <Chip
                label={`${site.total_queries} queries`}
                size="small"
                variant="outlined"
                color="default"
                sx={{ fontSize: '0.75rem' }}
              />
              {site.subdomains.length > 1 && (
                <Chip
                  label={`${site.subdomains.length} subdomains`}
                  size="small"
                  variant="outlined"
                  color="info"
                  sx={{ fontSize: '0.75rem' }}
                />
              )}
              <Chip
                label={site.blocked ? 'Blocked' : 'Allowed'}
                size="small"
                color={site.blocked ? 'error' : 'success'}
                variant="outlined"
                sx={{ fontSize: '0.75rem' }}
              />
            </Stack>
          }
          secondary={
            <Typography variant="caption" color="text.secondary">
              Last seen: {formatTime(site.last_seen)}
            </Typography>
          }
        />
        {site.subdomains.length > 1 && (
          <IconButton size="small" sx={{ ml: 1 }}>
            {expanded ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
          </IconButton>
        )}
      </ListItem>
      {site.subdomains.length > 1 && (
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Box sx={{ pl: 7, pr: 2, pb: 1, backgroundColor: 'action.hover' }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
              Subdomains:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
              {site.subdomains.map((sub) => (
                <Chip
                  key={sub}
                  label={sub}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem', height: 22 }}
                />
              ))}
            </Box>
          </Box>
        </Collapse>
      )}
    </>
  );
}

export default function DnsSitesView() {
  const {
    sites,
    loading,
    totalSites,
    noiseFiltered,
    blockedOnly,
    setBlockedOnly,
    filterNoise,
    setFilterNoise,
    refetch,
  } = useDnsSites();

  if (loading && sites.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper variant="outlined" sx={{ maxHeight: 500, display: 'flex', flexDirection: 'column' }}>
      {/* Header / Controls */}
      <Stack
        direction="row"
        alignItems="center"
        spacing={1}
        sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: 'divider', flexWrap: 'wrap' }}
      >
        <FormControlLabel
          control={
            <Switch
              checked={blockedOnly}
              onChange={(e) => setBlockedOnly(e.target.checked)}
              size="small"
            />
          }
          label={<Typography variant="body2">Blocked only</Typography>}
        />
        <FormControlLabel
          control={
            <Switch
              checked={filterNoise}
              onChange={(e) => setFilterNoise(e.target.checked)}
              size="small"
            />
          }
          label={
            <Stack direction="row" alignItems="center" spacing={0.5}>
              <FilterAltOffIcon sx={{ fontSize: 16 }} />
              <Typography variant="body2">Hide noise</Typography>
            </Stack>
          }
        />

        <Box sx={{ flex: 1 }} />

        <Typography variant="caption" color="text.secondary">
          {totalSites} sites
          {noiseFiltered > 0 && ` · ${noiseFiltered} noise filtered`}
        </Typography>

        <Tooltip title="Refresh">
          <IconButton size="small" onClick={refetch} disabled={loading}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>

      {/* Sites list */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {sites.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: 200,
              color: 'text.secondary',
            }}
          >
            <Typography variant="body2">No sites found for the selected period.</Typography>
          </Box>
        ) : (
          <List dense disablePadding>
            {sites.map((site, index) => (
              <Box key={site.root_domain}>
                <SiteRow site={site} />
                {index < sites.length - 1 && <Divider component="li" />}
              </Box>
            ))}
          </List>
        )}
      </Box>
    </Paper>
  );
}
