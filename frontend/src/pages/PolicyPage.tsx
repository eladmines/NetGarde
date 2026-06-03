import { useCallback, useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import Chip from '@mui/material/Chip';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import Button from '@mui/material/Button';
import RefreshIcon from '@mui/icons-material/Refresh';
import { policyApi } from '../features/policy/config/api';
import { PolicyPack, PolicyProfile, PolicySyncStatus } from '../features/policy/types/policy';
import { formatShortDateTime } from '../shared/utils/dateUtils';

const SYNC_POLL_MS = 8000;

function syncStatusLabel(status: PolicySyncStatus | null): string {
  if (!status?.last_sync_at) {
    return 'Not applied to dnsmasq yet';
  }
  const when = formatShortDateTime(status.last_sync_at);
  if (status.last_success === false) {
    return `Last apply failed · ${when}`;
  }
  return `Last applied · ${when}`;
}

export default function PolicyPage() {
  const [packs, setPacks] = useState<PolicyPack[]>([]);
  const [profiles, setProfiles] = useState<PolicyProfile[]>([]);
  const [syncStatus, setSyncStatus] = useState<PolicySyncStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [savingSlug, setSavingSlug] = useState<string | null>(null);
  const [refreshingSlug, setRefreshingSlug] = useState<string | null>(null);
  const [applying, setApplying] = useState(false);

  const loadSyncStatus = useCallback(async () => {
    try {
      const status = await policyApi.getSyncStatus();
      setSyncStatus(status);
    } catch {
      /* optional on older backends */
    }
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, pr] = await Promise.all([policyApi.listPacks(), policyApi.listProfiles()]);
      setPacks(p);
      setProfiles(pr);
      await loadSyncStatus();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load policy');
    } finally {
      setLoading(false);
    }
  }, [loadSyncStatus]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    const id = window.setInterval(loadSyncStatus, SYNC_POLL_MS);
    return () => window.clearInterval(id);
  }, [loadSyncStatus]);

  const refreshPackList = async (pack: PolicyPack) => {
    setRefreshingSlug(pack.slug);
    setError(null);
    try {
      const result = await policyApi.refreshPack(pack.slug);
      setPacks((prev) =>
        prev.map((p) =>
          p.slug === pack.slug ? { ...p, domain_count: result.domain_count } : p,
        ),
      );
      setInfo(result.message);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to refresh pack list');
    } finally {
      setRefreshingSlug(null);
    }
  };

  const togglePack = async (pack: PolicyPack) => {
    setSavingSlug(pack.slug);
    setInfo(null);
    try {
      const updated = await policyApi.updatePack(pack.slug, !pack.enabled_globally);
      setPacks((prev) => prev.map((p) => (p.slug === updated.slug ? updated : p)));
      setInfo(
        `${updated.name} saved. Enforcement sync runs automatically (dns-sync + dnsmasq reload).`,
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to update pack');
    } finally {
      setSavingSlug(null);
    }
  };

  const applyNow = async () => {
    setApplying(true);
    setError(null);
    try {
      const result = await policyApi.applyPolicy();
      setInfo(result.message);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to queue policy apply');
    } finally {
      setApplying(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 960 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h5" sx={{ mb: 0.5, fontWeight: 600 }}>
            Policy
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Changes sync to dnsmasq automatically via the host listener.
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
            {syncStatusLabel(syncStatus)}
          </Typography>
        </Box>
        <Button
          size="small"
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={applyNow}
          disabled={applying}
        >
          Apply now
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {info && (
        <Alert severity="info" sx={{ mb: 2 }} onClose={() => setInfo(null)}>
          {info}
        </Alert>
      )}

      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
          List packs (network-wide)
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
          Lists are downloaded from curated upstream sources (large blocklists, like Social). Use
          Refresh to update counts; toggling On queues an immediate DNS policy sync.
        </Typography>
        <Stack spacing={1}>
          {packs.map((pack) => (
            <Stack
              key={pack.slug}
              direction="row"
              alignItems="center"
              justifyContent="space-between"
              sx={{ py: 0.5 }}
            >
              <Box>
                <Typography variant="body2" fontWeight={600}>
                  {pack.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {pack.description} · {pack.domain_count} domains
                </Typography>
              </Box>
              <Stack direction="row" spacing={1} alignItems="center">
                <Button
                  size="small"
                  variant="text"
                  startIcon={<RefreshIcon />}
                  disabled={refreshingSlug === pack.slug}
                  onClick={() => refreshPackList(pack)}
                >
                  Refresh
                </Button>
                <FormControlLabel
                  control={
                    <Switch
                      checked={pack.enabled_globally}
                      disabled={savingSlug === pack.slug}
                      onChange={() => togglePack(pack)}
                    />
                  }
                  label={pack.enabled_globally ? 'On' : 'Off'}
                />
              </Stack>
            </Stack>
          ))}
        </Stack>
      </Paper>

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
          Device profiles
        </Typography>
        <Stack spacing={2} divider={<Divider flexItem />}>
          {profiles.map((profile) => (
            <Box key={profile.slug}>
              <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                <Typography variant="body1" fontWeight={600}>
                  {profile.name}
                </Typography>
                <Chip label={profile.slug} size="small" variant="outlined" />
                <Chip label={`Sensitivity: ${profile.behavior_sensitivity}`} size="small" />
                {profile.quarantine_on_abnormal && (
                  <Chip
                    label={`Quarantine ${profile.quarantine_hours}h`}
                    size="small"
                    color="warning"
                    variant="outlined"
                  />
                )}
              </Stack>
              {profile.description && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {profile.description}
                </Typography>
              )}
              <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mt: 1 }}>
                {profile.enabled_pack_slugs.map((slug) => (
                  <Chip key={slug} label={slug} size="small" />
                ))}
              </Stack>
              {profile.schedule_rules.length > 0 && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Schedule: {profile.schedule_rules[0].start}–{profile.schedule_rules[0].end} (
                  {profile.schedule_rules[0].pack_slugs.join(', ')})
                </Typography>
              )}
            </Box>
          ))}
        </Stack>
      </Paper>
    </Box>
  );
}
