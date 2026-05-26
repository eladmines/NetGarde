import { useCallback, useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Chip from '@mui/material/Chip';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import { devicesApi } from '../config/api';
import {
  BehaviorProfile,
  ClientBlockedDomain,
  Device,
  DeviceSecurityPolicy,
} from '../types/device';
import { DnsAlert } from '../../dns-queries/types/dnsQuery';
import BaselineSummary from './BaselineSummary';
import { formatShortDateTime } from '../../../shared/utils/dateUtils';

interface ClientProfileDetailProps {
  device: Device;
}

export default function ClientProfileDetail({ device }: ClientProfileDetailProps) {
  const [profile, setProfile] = useState<BehaviorProfile | null>(null);
  const [policy, setPolicy] = useState<DeviceSecurityPolicy | null>(null);
  const [blocks, setBlocks] = useState<ClientBlockedDomain[]>([]);
  const [events, setEvents] = useState<DnsAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, pol, b, ev] = await Promise.all([
        devicesApi.getBehaviorProfile(device.id),
        devicesApi.getSecurityPolicy(device.id),
        devicesApi.listClientBlocks(device.id),
        devicesApi.getBehaviorEvents(device.id, 1, 10),
      ]);
      setProfile(p);
      setPolicy(pol);
      setBlocks(b);
      setEvents(ev.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  }, [device.id]);

  useEffect(() => {
    load();
  }, [load]);

  const toggleAutoBlock = async () => {
    if (!policy) return;
    setSaving(true);
    try {
      const updated = await devicesApi.updateSecurityPolicy(device.id, {
        auto_block_enabled: !policy.auto_block_enabled,
      });
      setPolicy(updated);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to update policy');
    } finally {
      setSaving(false);
    }
  };

  const revokeBlock = async (blockId: number) => {
    try {
      await devicesApi.revokeClientBlock(device.id, blockId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to revoke block');
    }
  };

  const label = device.hostname || device.client_ip;

  return (
    <Paper variant="outlined" sx={{ p: 3, minHeight: 400 }}>
      <Stack spacing={3}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
          <Box>
            <Typography variant="h5">{label}</Typography>
            <Typography variant="body2" color="text.secondary">
              {device.client_ip}
              {device.mac_address ? ` · ${device.mac_address}` : ''}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Source: {device.source}
            </Typography>
          </Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip
              label={profile?.profile_ready ? 'Baseline ready' : 'Learning'}
              color={profile?.profile_ready ? 'success' : 'default'}
              variant="outlined"
            />
            {profile?.last_score != null && (
              <Chip label={`Score: ${profile.last_score}`} color="warning" variant="outlined" />
            )}
            <Button size="small" onClick={load}>
              Refresh
            </Button>
          </Stack>
        </Stack>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}
        {error && <Alert severity="error">{error}</Alert>}

        {!loading && profile && (
          <>
            <Box>
              <Typography variant="subtitle1" sx={{ mb: 1.5 }}>
                Behavior baseline
              </Typography>
              {profile.profile_ready && Object.keys(profile.baseline).length > 0 ? (
                <BaselineSummary baseline={profile.baseline} />
              ) : (
                <Alert severity="info" variant="outlined">
                  Profile is still learning. NetGarde needs roughly 3 days of DNS activity and 500+
                  queries before a baseline is computed.
                </Alert>
              )}
              {profile.last_scored_at && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Last scored: {formatShortDateTime(profile.last_scored_at)}
                </Typography>
              )}
            </Box>

            {policy && (
              <Box>
                <Typography variant="subtitle1" sx={{ mb: 1 }}>
                  Security policy
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={policy.auto_block_enabled}
                      onChange={toggleAutoBlock}
                      disabled={saving}
                    />
                  }
                  label="Auto-block domains on abnormal behavior"
                />
                <Typography variant="body2" color="text.secondary">
                  Threshold: {policy.auto_block_threshold} · Max blocks/day:{' '}
                  {policy.max_blocks_per_day}
                </Typography>
              </Box>
            )}

            {blocks.length > 0 && (
              <Box>
                <Typography variant="subtitle1" sx={{ mb: 1 }}>
                  Active per-device blocks
                </Typography>
                <List dense disablePadding>
                  {blocks.map((b) => (
                    <Box key={b.id}>
                      <ListItem
                        secondaryAction={
                          <Button size="small" onClick={() => revokeBlock(b.id)}>
                            Revoke
                          </Button>
                        }
                      >
                        <ListItemText
                          primary={b.domain}
                          secondary={
                            b.expires_at
                              ? `Expires ${formatShortDateTime(b.expires_at)} · score ${b.score ?? '—'}`
                              : `score ${b.score ?? '—'}`
                          }
                        />
                      </ListItem>
                      <Divider />
                    </Box>
                  ))}
                </List>
              </Box>
            )}

            <Box>
              <Typography variant="subtitle1" sx={{ mb: 1 }}>
                Recent behavior alerts
              </Typography>
              {events.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No behavior anomalies recorded for this device.
                </Typography>
              ) : (
                <List dense disablePadding>
                  {events.map((ev) => (
                    <Box key={ev.id}>
                      <ListItem alignItems="flex-start">
                        <ListItemText
                          primary={ev.domain || ev.root_domain || '—'}
                          secondary={
                            <>
                              {formatShortDateTime(ev.timestamp)}
                              {ev.message ? ` — ${ev.message}` : ''}
                            </>
                          }
                        />
                      </ListItem>
                      <Divider />
                    </Box>
                  ))}
                </List>
              )}
            </Box>
          </>
        )}
      </Stack>
    </Paper>
  );
}
