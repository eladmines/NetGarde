import { useState } from 'react';
import { styled, useTheme } from '@mui/material/styles';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import MuiToolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import { alpha } from '@mui/material/styles';
import MenuRoundedIcon from '@mui/icons-material/MenuRounded';
import DashboardRoundedIcon from '@mui/icons-material/DashboardRounded';
import NotificationsRoundedIcon from '@mui/icons-material/NotificationsRounded';
import SideMenuMobile from './SideMenuMobile';
import MenuButton from './MenuButton';
import ColorModeIconDropdown from '../../../shared/theme/ColorModeIconDropdown';
import {
  navbarBackground,
  navbarColorModeButtonSx,
  navbarIconButtonSx,
  NAVBAR_HEIGHT,
} from '../../../shared/theme/navigationChrome';

const Toolbar = styled(MuiToolbar)({
  width: '100%',
  padding: '12px',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'start',
  justifyContent: 'center',
  gap: '12px',
  flexShrink: 0,
});

const AzureToolbar = styled(MuiToolbar)(({ theme }) => ({
  minHeight: `${NAVBAR_HEIGHT}px !important`,
  padding: '0 16px !important',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  backgroundColor: navbarBackground(theme),
  borderBottom: `1px solid ${alpha(
    theme.palette.common.white,
    theme.palette.mode === 'dark' ? 0.08 : 0.1,
  )}`,
}));

export default function AppNavbar() {
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const onDarkNavbar = theme.palette.mode === 'dark';

  const toggleDrawer = (newOpen: boolean) => () => {
    setOpen(newOpen);
  };

  const navbarFg = onDarkNavbar ? theme.palette.text.primary : '#ffffff';
  const navbarIconBg = onDarkNavbar
    ? alpha(theme.palette.common.white, 0.08)
    : 'rgba(255, 255, 255, 0.1)';

  return (
    <>
      <AppBar
        position="fixed"
        sx={{
          display: { xs: 'auto', md: 'none' },
          boxShadow: 0,
          bgcolor: 'background.paper',
          backgroundImage: 'none',
          borderBottom: '1px solid',
          borderColor: 'divider',
          top: 'var(--template-frame-height, 0px)',
        }}
      >
        <Toolbar variant="regular">
          <Stack
            direction="row"
            sx={{
              alignItems: 'center',
              flexGrow: 1,
              width: '100%',
              gap: 1,
            }}
          >
            <Stack
              direction="row"
              spacing={1}
              sx={{ justifyContent: 'center', mr: 'auto' }}
            >
              <CustomIcon />
              <Typography variant="h4" component="h1" sx={{ color: 'text.primary' }}>
                Dashboard
              </Typography>
            </Stack>
            <ColorModeIconDropdown />
            <MenuButton aria-label="menu" onClick={toggleDrawer(true)}>
              <MenuRoundedIcon />
            </MenuButton>
            <SideMenuMobile open={open} toggleDrawer={toggleDrawer} />
          </Stack>
        </Toolbar>
      </AppBar>

      <AppBar
        position="fixed"
        sx={{
          display: { xs: 'none', md: 'block' },
          top: 0,
          left: 0,
          right: 0,
          zIndex: (t) => t.zIndex.drawer + 1,
          backgroundColor: navbarBackground(theme),
          boxShadow: (t) =>
            t.palette.mode === 'dark'
              ? '0 2px 8px rgba(0,0,0,0.45)'
              : '0 2px 4px rgba(0,0,0,0.1)',
        }}
      >
        <AzureToolbar>
          <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center' }}>
            <Box
              sx={{
                width: '32px',
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '4px',
                backgroundColor: navbarIconBg,
              }}
            >
              <DashboardRoundedIcon sx={{ color: navbarFg, fontSize: '20px' }} />
            </Box>
            <Typography
              variant="h6"
              component="div"
              sx={{
                color: navbarFg,
                fontWeight: 600,
                fontSize: '1.125rem',
                letterSpacing: '0.01em',
              }}
            >
              NetGarde
            </Typography>
          </Stack>

          <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
            <MenuButton aria-label="notifications" sx={navbarIconButtonSx(theme)}>
              <NotificationsRoundedIcon />
            </MenuButton>
            <ColorModeIconDropdown sx={navbarColorModeButtonSx(theme)} />
            <Avatar
              sizes="small"
              alt="NetGarde"
              sx={{
                width: 32,
                height: 32,
                border: '2px solid',
                borderColor: onDarkNavbar
                  ? alpha(theme.palette.common.white, 0.2)
                  : 'rgba(255, 255, 255, 0.3)',
                cursor: 'pointer',
                '&:hover': {
                  borderColor: onDarkNavbar
                    ? alpha(theme.palette.common.white, 0.35)
                    : 'rgba(255, 255, 255, 0.5)',
                },
              }}
            />
          </Stack>
        </AzureToolbar>
      </AppBar>
    </>
  );
}

export function CustomIcon() {
  return (
    <Box
      sx={{
        width: '1.5rem',
        height: '1.5rem',
        bgcolor: 'black',
        borderRadius: '999px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        alignSelf: 'center',
        backgroundImage:
          'linear-gradient(135deg, hsl(210, 98%, 60%) 0%, hsl(210, 100%, 35%) 100%)',
        color: 'hsla(210, 100%, 95%, 0.9)',
        border: '1px solid',
        borderColor: 'hsl(210, 100%, 55%)',
        boxShadow: 'inset 0 2px 5px rgba(255, 255, 255, 0.3)',
      }}
    >
      <DashboardRoundedIcon color="inherit" sx={{ fontSize: '1rem' }} />
    </Box>
  );
}
