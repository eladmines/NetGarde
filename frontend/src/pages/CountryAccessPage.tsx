import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import RefreshIcon from '@mui/icons-material/Refresh';
import GeoCountryPolicyEditor from '../features/policy/components/GeoCountryPolicyEditor';
import { usePolicyDnsSync } from '../features/policy/hooks/usePolicyDnsSync';

export default function CountryAccessPage() {
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

      <Alert severity="info" sx={{ mb: 2 }}>
        VPN login blocks take effect on the next enroll attempt. Destination country rules need{' '}
        <strong>Save country blocks</strong> then <strong>Apply now</strong> to update dnsmasq.
      </Alert>

      <GeoCountryPolicyEditor />
    </Box>
  );
}
