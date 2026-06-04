import { useCallback, useEffect, useMemo, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import Chip from '@mui/material/Chip';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import CircularProgress from '@mui/material/CircularProgress';
import SaveIcon from '@mui/icons-material/Save';
import { policyApi } from '../config/api';
import {
  CountryChoice,
  DestinationCountryRuleUpdate,
  ForbiddenCountryPolicy,
  GeoCountryPolicyUpdate,
} from '../types/policy';
import { countryFlagEmoji, countryLabel } from '../../devices/utils/countryDisplay';

type RuleRow = { user_country: string; blocked_countries: string[] };

export default function GeoCountryPolicyEditor() {
  const [choices, setChoices] = useState<CountryChoice[]>([]);
  const [policy, setPolicy] = useState<ForbiddenCountryPolicy | null>(null);
  const [vpnLoginEnabled, setVpnLoginEnabled] = useState(true);
  const [destEnabled, setDestEnabled] = useState(true);
  const [vpnDenied, setVpnDenied] = useState<string[]>([]);
  const [destRules, setDestRules] = useState<RuleRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const [addVpnCountry, setAddVpnCountry] = useState<CountryChoice | null>(null);
  const [addUserCountry, setAddUserCountry] = useState<CountryChoice | null>(null);
  const [addDestCountry, setAddDestCountry] = useState<CountryChoice | null>(null);
  const [addDestForUser, setAddDestForUser] = useState<string>('IL');

  const choiceByCode = useMemo(() => {
    const m = new Map<string, CountryChoice>();
    for (const c of choices) {
      m.set(c.code, c);
    }
    return m;
  }, [choices]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [ch, pol] = await Promise.all([
        policyApi.listGeoCountryChoices(),
        policyApi.getForbiddenCountries(),
      ]);
      setChoices(ch);
      setPolicy(pol);
      setVpnLoginEnabled(pol.vpn_login_block_enabled);
      setDestEnabled(pol.enabled);
      setVpnDenied([...pol.blocked_vpn_login_countries]);
      setDestRules(
        pol.rules.map((r) => ({
          user_country: r.user_country,
          blocked_countries: [...r.blocked_countries],
        })),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load geo policy');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const addVpnDenied = () => {
    if (!addVpnCountry) return;
    if (!vpnDenied.includes(addVpnCountry.code)) {
      setVpnDenied((prev) => [...prev, addVpnCountry.code].sort());
    }
    setAddVpnCountry(null);
  };

  const addDestinationBlock = () => {
    if (!addDestCountry || !addUserCountry) return;
    const user = addUserCountry.code;
    const dest = addDestCountry.code;
    setDestRules((prev) => {
      const row = prev.find((r) => r.user_country === user);
      if (row) {
        if (!row.blocked_countries.includes(dest)) {
          row.blocked_countries = [...row.blocked_countries, dest].sort();
        }
        return [...prev];
      }
      return [...prev, { user_country: user, blocked_countries: [dest] }].sort((a, b) =>
        a.user_country.localeCompare(b.user_country),
      );
    });
    setAddDestCountry(null);
    setAddUserCountry(choiceByCode.get(addDestForUser) ?? addUserCountry);
  };

  const save = async () => {
    setSaving(true);
    setError(null);
    setInfo(null);
    const body: GeoCountryPolicyUpdate = {
      vpn_login_block_enabled: vpnLoginEnabled,
      destination_rules_enabled: destEnabled,
      vpn_login_denied_countries: vpnDenied,
      destination_rules: destRules.map(
        (r): DestinationCountryRuleUpdate => ({
          user_country: r.user_country,
          blocked_countries: r.blocked_countries,
        }),
      ),
    };
    try {
      const updated = await policyApi.updateForbiddenCountries(body);
      setPolicy(updated);
      setInfo('Geo country rules saved. Click Apply now to push DNS blocks to dnsmasq.');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
        <CircularProgress size={28} />
      </Box>
    );
  }

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 0.5 }}>
        Block countries (manual)
      </Typography>
      <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1.5 }}>
        User location = VPN login GeoIP. Save here overrides env defaults. Deny enroll blocks
        countries from joining; destination rules block ccTLDs for matching login countries.
      </Typography>

      {policy && !policy.managed_in_database && (
        <Alert severity="info" sx={{ mb: 1.5 }}>
          Showing env defaults until you save. After save, rules are stored in the database.
        </Alert>
      )}
      {error && (
        <Alert severity="error" sx={{ mb: 1.5 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {info && (
        <Alert severity="success" sx={{ mb: 1.5 }} onClose={() => setInfo(null)}>
          {info}
        </Alert>
      )}

      <FormControlLabel
        control={
          <Switch checked={vpnLoginEnabled} onChange={(e) => setVpnLoginEnabled(e.target.checked)} />
        }
        label="Deny VPN enrollment from blocked countries"
        sx={{ mb: 1 }}
      />
      <Stack direction="row" flexWrap="wrap" gap={0.75} sx={{ mb: 1 }}>
        {vpnDenied.map((code) => (
          <Chip
            key={code}
            label={countryLabel(code, choiceByCode.get(code)?.name)}
            icon={<span>{countryFlagEmoji(code)}</span>}
            onDelete={() => setVpnDenied((prev) => prev.filter((c) => c !== code))}
            size="small"
          />
        ))}
      </Stack>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mb: 2 }} alignItems="flex-start">
        <Autocomplete
          size="small"
          sx={{ minWidth: 220, flex: 1 }}
          options={choices}
          value={addVpnCountry}
          onChange={(_, v) => setAddVpnCountry(v)}
          getOptionLabel={(o) => countryLabel(o.code, o.name)}
          renderInput={(params) => <TextField {...params} label="Add blocked login country" />}
        />
        <Button size="small" variant="outlined" onClick={addVpnDenied} disabled={!addVpnCountry}>
          Add
        </Button>
      </Stack>

      <FormControlLabel
        control={
          <Switch checked={destEnabled} onChange={(e) => setDestEnabled(e.target.checked)} />
        }
        label="Block destination countries for users in…"
        sx={{ mb: 1 }}
      />
      <Stack spacing={1} sx={{ mb: 1 }}>
        {destRules.map((rule) => (
          <Box key={rule.user_country}>
            <Typography variant="body2" sx={{ mb: 0.5 }}>
              Login {countryLabel(rule.user_country, choiceByCode.get(rule.user_country)?.name)}{' '}
              → block:
            </Typography>
            <Stack direction="row" flexWrap="wrap" gap={0.75}>
              {rule.blocked_countries.map((code) => (
                <Chip
                  key={code}
                  size="small"
                  label={countryLabel(code, choiceByCode.get(code)?.name)}
                  icon={<span>{countryFlagEmoji(code)}</span>}
                  onDelete={() =>
                    setDestRules((prev) =>
                      prev
                        .map((r) =>
                          r.user_country === rule.user_country
                            ? {
                                ...r,
                                blocked_countries: r.blocked_countries.filter((c) => c !== code),
                              }
                            : r,
                        )
                        .filter((r) => r.blocked_countries.length > 0),
                    )
                  }
                />
              ))}
            </Stack>
          </Box>
        ))}
      </Stack>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mb: 2 }} flexWrap="wrap">
        <Autocomplete
          size="small"
          sx={{ minWidth: 180, flex: 1 }}
          options={choices}
          value={addUserCountry ?? choiceByCode.get(addDestForUser) ?? null}
          onChange={(_, v) => {
            setAddUserCountry(v);
            if (v) setAddDestForUser(v.code);
          }}
          getOptionLabel={(o) => countryLabel(o.code, o.name)}
          renderInput={(params) => <TextField {...params} label="When user login country" />}
        />
        <Autocomplete
          size="small"
          sx={{ minWidth: 180, flex: 1 }}
          options={choices}
          value={addDestCountry}
          onChange={(_, v) => setAddDestCountry(v)}
          getOptionLabel={(o) => countryLabel(o.code, o.name)}
          renderInput={(params) => <TextField {...params} label="Block destination" />}
        />
        <Button
          size="small"
          variant="outlined"
          onClick={addDestinationBlock}
          disabled={!addDestCountry || !addUserCountry}
        >
          Add rule
        </Button>
      </Stack>

      <Button
        variant="contained"
        size="small"
        startIcon={saving ? <CircularProgress size={16} color="inherit" /> : <SaveIcon />}
        onClick={save}
        disabled={saving}
      >
        Save country blocks
      </Button>
    </Paper>
  );
}
