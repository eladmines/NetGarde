import { useRef, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import RefreshIcon from '@mui/icons-material/Refresh';
import SaveIcon from '@mui/icons-material/Save';
import GeoCountryPolicyEditor, {
  GeoCountryPolicyEditorHandle,
} from '../features/policy/components/GeoCountryPolicyEditor';
import { usePolicyDnsSync } from '../features/policy/hooks/usePolicyDnsSync';

export default function CountryAccessPage() {
  const editorRef = useRef<GeoCountryPolicyEditorHandle>(null);
  const [savingCountries, setSavingCountries] = useState(false);
  const {
    syncStatusLabel,
    applying,
    applyError,
    setApplyError,
    applyInfo,
    setApplyInfo,
    applyNow,
  } = usePolicyDnsSync();

  return (
    <Box sx={{ maxWidth: 960 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h5" sx={{ mb: 0.5, fontWeight: 600 }}>
            Country access
          </Typography>
          <Typography variant="body2" color="text.secondary">
            VPN login GeoIP controls who can enroll. Destination rules block country TLDs in DNS
            for matching login countries.
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
            {syncStatusLabel}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1} sx={{ flexShrink: 0 }}>
          <Button
            size="small"
            variant="outlined"
            startIcon={
              savingCountries ? <CircularProgress size={14} color="inherit" /> : <SaveIcon />
            }
            onClick={() => void editorRef.current?.save()}
            disabled={savingCountries}
          >
            Save country blocks
          </Button>
          <Button
            size="small"
            variant="outlined"
            startIcon={applying ? <CircularProgress size={14} color="inherit" /> : <RefreshIcon />}
            onClick={applyNow}
            disabled={applying}
          >
            Apply now
          </Button>
        </Stack>
      </Stack>

      {applyError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setApplyError(null)}>
          {applyError}
        </Alert>
      )}
      {applyInfo && (
        <Alert severity="info" sx={{ mb: 2 }} onClose={() => setApplyInfo(null)}>
          {applyInfo}
        </Alert>
      )}

      <GeoCountryPolicyEditor ref={editorRef} onSavingChange={setSavingCountries} />
    </Box>
  );
}
