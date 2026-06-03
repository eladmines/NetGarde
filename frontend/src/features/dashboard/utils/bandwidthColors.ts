import type { Theme } from '@mui/material/styles';
import type { SxProps } from '@mui/material/styles';

/** Download = incoming (↓), upload = outgoing (↑) — distinct on light and dark themes. */
export function getBandwidthColors(theme: Theme) {
  return {
    download: theme.palette.success.main,
    downloadMuted: theme.palette.success.dark,
    upload: theme.palette.warning.main,
    uploadMuted: theme.palette.warning.dark,
  };
}

export function downloadChipSx(theme: Theme): SxProps<Theme> {
  const c = getBandwidthColors(theme);
  return {
    borderColor: c.download,
    color: c.download,
    '& .MuiChip-icon': { color: c.download },
    bgcolor: `${c.download}14`,
  };
}

export function uploadChipSx(theme: Theme): SxProps<Theme> {
  const c = getBandwidthColors(theme);
  return {
    borderColor: c.upload,
    color: c.upload,
    '& .MuiChip-icon': { color: c.upload },
    bgcolor: `${c.upload}14`,
  };
}

export function downloadProgressSx(theme: Theme): SxProps<Theme> {
  const c = getBandwidthColors(theme);
  return {
    height: 6,
    borderRadius: 1,
    bgcolor: `${c.download}22`,
    '& .MuiLinearProgress-bar': { bgcolor: c.download, borderRadius: 1 },
  };
}

export function uploadProgressSx(theme: Theme): SxProps<Theme> {
  const c = getBandwidthColors(theme);
  return {
    height: 6,
    borderRadius: 1,
    bgcolor: `${c.upload}22`,
    '& .MuiLinearProgress-bar': { bgcolor: c.upload, borderRadius: 1 },
  };
}
