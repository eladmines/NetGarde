import { forwardRef, useCallback, useEffect, useImperativeHandle, useMemo, useState } from 'react';
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
import { policyApi } from '../config/api';
import {
  CountryChoice,
  DestinationCountryRuleUpdate,
  GeoCountryPolicyUpdate,
} from '../types/policy';
import { countryFlagEmoji, countryLabel } from '../../devices/utils/countryDisplay';

type RuleRow = { user_country: string; blocked_countries: string[] };

const countryAutocompleteSx = {
  width: '100%',
  '& .MuiOutlinedInput-root': {
    pr: '58px !important',
  },
  '& .MuiAutocomplete-endAdornment': {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    position: 'absolute',
    right: 8,
    top: '50%',
    transform: 'translateY(-50%)',
    gap: 0.25,
  },
  '& .MuiAutocomplete-clearIndicator': {
    order: 1,
    p: 0.5,
  },
  '& .MuiAutocomplete-popupIndicator': {
    order: 2,
    p: 0.5,
  },
} as const;

function CountryAutocomplete({
  label,
  options,
  value,
  onChange,
  minWidth = 200,
}: {
  label: string;
  options: CountryChoice[];
  value: CountryChoice | null;
  onChange: (value: CountryChoice | null) => void;
  minWidth?: number;
}) {
  return (
    <Box sx={{ minWidth, flex: 1, width: '100%' }}>
      <Typography variant="caption" color="text.secondary" component="label" display="block" sx={{ mb: 0.75 }}>
        {label}
      </Typography>
      <Autocomplete
        fullWidth
        size="small"
        options={options}
        value={value}
        onChange={(_, v) => onChange(v)}
        getOptionLabel={(o) => countryLabel(o.code, o.name)}
        sx={countryAutocompleteSx}
        slotProps={{
          clearIndicator: { size: 'small' },
          popupIndicator: { size: 'small' },
        }}
        renderInput={(params) => (
          <TextField
            {...params}
            hiddenLabel
            placeholder={value ? undefined : 'Select country'}
            slotProps={{
              input: {
                ...params.InputProps,
                sx: { flexWrap: 'nowrap' },
              },
            }}
          />
        )}
      />
    </Box>
  );
}

export type GeoCountryPolicyEditorHandle = {
  save: () => Promise<void>;
};

type GeoCountryPolicyEditorProps = {
  onSavingChange?: (saving: boolean) => void;
};

const GeoCountryPolicyEditor = forwardRef<GeoCountryPolicyEditorHandle, GeoCountryPolicyEditorProps>(
  function GeoCountryPolicyEditor({ onSavingChange }, ref) {
  const [choices, setChoices] = useState<CountryChoice[]>([]);
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
    setAddUserCountry(null);
  };

  const save = useCallback(async () => {
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
      await policyApi.updateForbiddenCountries(body);
      setInfo('Country rules saved.');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  }, [vpnLoginEnabled, destEnabled, vpnDenied, destRules]);

  useImperativeHandle(ref, () => ({ save }), [save]);

  useEffect(() => {
    onSavingChange?.(saving);
  }, [saving, onSavingChange]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
        <CircularProgress size={28} />
      </Box>
    );
  }

  return (
    <Paper variant="outlined" sx={{ p: 2.5 }}>
      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
        Block countries (manual)
      </Typography>

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

      <Box sx={{ mb: 3 }}>
        <FormControlLabel
          control={
            <Switch checked={vpnLoginEnabled} onChange={(e) => setVpnLoginEnabled(e.target.checked)} />
          }
          label="Deny VPN enrollment from blocked countries"
          sx={{ mb: 1.5, display: 'block' }}
        />
        <Stack direction="row" flexWrap="wrap" gap={0.75} sx={{ mb: 1.5, minHeight: 28 }}>
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
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={1.5}
          alignItems={{ xs: 'stretch', sm: 'flex-end' }}
        >
          <CountryAutocomplete
            label="Blocked login country"
            options={choices}
            value={addVpnCountry}
            onChange={setAddVpnCountry}
            minWidth={240}
          />
          <Button
            size="small"
            variant="outlined"
            onClick={addVpnDenied}
            disabled={!addVpnCountry}
            sx={{ flexShrink: 0, alignSelf: { sm: 'flex-end' }, mb: { sm: 0.25 } }}
          >
            Add
          </Button>
        </Stack>
      </Box>

      <Box>
        <FormControlLabel
          control={
            <Switch checked={destEnabled} onChange={(e) => setDestEnabled(e.target.checked)} />
          }
          label="Block destination countries for users in…"
          sx={{ mb: 1.5, display: 'block' }}
        />
      <Stack spacing={2} sx={{ mb: 2 }}>
        {destRules.map((rule) => (
          <Box key={rule.user_country}>
            <Typography variant="body2" sx={{ mb: 0.75 }}>
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
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={1.5}
        alignItems={{ xs: 'stretch', sm: 'flex-end' }}
        sx={{ mb: 2 }}
      >
        <CountryAutocomplete
          label="User login country"
          options={choices}
          value={addUserCountry}
          onChange={setAddUserCountry}
        />
        <CountryAutocomplete
          label="Destination to block"
          options={choices}
          value={addDestCountry}
          onChange={setAddDestCountry}
        />
        <Button
          size="small"
          variant="outlined"
          onClick={addDestinationBlock}
          disabled={!addDestCountry || !addUserCountry}
          sx={{ flexShrink: 0, alignSelf: { sm: 'flex-end' }, mb: { sm: 0.25 } }}
        >
          Add rule
        </Button>
      </Stack>
      </Box>
    </Paper>
  );
},
);

export default GeoCountryPolicyEditor;
