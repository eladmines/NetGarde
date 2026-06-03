import type { Theme } from '@mui/material/styles';
import type { SxProps } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';
import { brand } from './themePrimitives';

/** Azure-style accent in light mode; primary in dark mode. */
export const NAV_ACCENT_LIGHT = '#0078d4';

export const NAVBAR_HEIGHT = 48;

export function navbarBackground(theme: Theme): string {
  return theme.palette.mode === 'dark' ? brand[900] : NAV_ACCENT_LIGHT;
}

export function navAccentColor(theme: Theme): string {
  return theme.palette.mode === 'dark' ? theme.palette.primary.main : NAV_ACCENT_LIGHT;
}

export function navbarIconButtonSx(theme: Theme): SxProps<Theme> {
  const fg = theme.palette.mode === 'dark' ? theme.palette.text.secondary : 'rgba(255, 255, 255, 0.8)';
  const fgHover = theme.palette.mode === 'dark' ? theme.palette.text.primary : '#ffffff';
  const hoverBg =
    theme.palette.mode === 'dark'
      ? alpha(theme.palette.common.white, 0.08)
      : 'rgba(255, 255, 255, 0.1)';

  return {
    color: fg,
    '&:hover': {
      backgroundColor: hoverBg,
      color: fgHover,
    },
  };
}

export function navbarColorModeButtonSx(theme: Theme): SxProps<Theme> {
  return {
    ...navbarIconButtonSx(theme),
    border: '1px solid',
    borderColor:
      theme.palette.mode === 'dark'
        ? alpha(theme.palette.common.white, 0.12)
        : 'rgba(255, 255, 255, 0.25)',
  };
}

export function sidebarNavItemSx(theme: Theme, nested = false): SxProps<Theme> {
  const accent = navAccentColor(theme);
  const selectedBg = alpha(accent, theme.palette.mode === 'dark' ? 0.22 : 0.08);
  const selectedHoverBg = alpha(accent, theme.palette.mode === 'dark' ? 0.3 : 0.12);

  return {
    minHeight: 40,
    borderRadius: '4px',
    px: 1.5,
    py: 1,
    mx: 0.5,
    mb: 0.5,
    ...(nested ? { ml: 4 } : {}),
    position: 'relative',
    '&.Mui-selected': {
      backgroundColor: selectedBg,
      '&:hover': {
        backgroundColor: selectedHoverBg,
      },
      '&::before': {
        content: '""',
        position: 'absolute',
        left: 0,
        top: '50%',
        transform: 'translateY(-50%)',
        width: 3,
        height: 20,
        backgroundColor: accent,
        borderRadius: '0 2px 2px 0',
      },
    },
    '&:hover': {
      backgroundColor: theme.palette.action.hover,
    },
  };
}

export function sidebarSectionButtonSx(theme: Theme): SxProps<Theme> {
  return {
    minHeight: 40,
    borderRadius: '4px',
    px: 1.5,
    py: 1,
    mx: 0.5,
    mb: 0.5,
    '&:hover': {
      backgroundColor: theme.palette.action.hover,
    },
  };
}
