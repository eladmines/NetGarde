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
import { policyApi } from '../features/policy/config/api';
import { PolicyPack, PolicyProfile } from '../features/policy/types/policy';

export default function PolicyPage() {
  const [packs, setPacks] = useState<PolicyPack[]>([]);
  const [profiles, setProfiles] = useState<PolicyProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingSlug, setSavingSlug] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, pr] = await Promise.all([policyApi.listPacks(), policyApi.listProfiles()]);
      setPacks(p);
      setProfiles(pr);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load policy');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const togglePack = async (pack: PolicyPack) => {
    setSavingSlug(pack.slug);
    try {
      const updated = await policyApi.updatePack(pack.slug, !pack.enabled_globally);
      setPacks((prev) => prev.map((p) => (p.slug === updated.slug ? updated : p)));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to update pack');
    } finally {
      setSavingSlug(null);
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
      <Typography variant="h5" sx={{ mb: 1, fontWeight: 600 }}>
        Policy
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Category packs, device profiles (Kids / Teen / Work), schedules, and quarantine replace manual
        blocked-site lists.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
          List packs (network-wide)
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
          Enabled packs apply to every device, merged with each device&apos;s profile.
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
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Assign on Client profiles or at VPN enroll with{' '}
                <code>policy_profile_slug</code>.
              </Typography>
            </Box>
          ))}
        </Stack>
      </Paper>
    </Box>
  );
}
