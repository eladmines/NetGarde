import * as React from 'react';
import { styled } from '@mui/material/styles';
import Avatar from '@mui/material/Avatar';
import MuiDrawer, { drawerClasses } from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import MenuContent from './MenuContent';
import CardAlert from './CardAlert';
import OptionsMenu from './OptionsMenu';
import './SideMenu.css';

const drawerWidth = 220;
const collapsedWidth = 64;

const Drawer = styled(MuiDrawer, {
  shouldForwardProp: (prop) => prop !== 'open',
})<{ open?: boolean }>(({ theme, open }) => ({
  width: open ? drawerWidth : collapsedWidth,
  flexShrink: 0,
  whiteSpace: 'nowrap',
  boxSizing: 'border-box',
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  [`& .${drawerClasses.paper}`]: {
    width: open ? drawerWidth : collapsedWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
    overflowX: 'hidden',
    marginTop: '48px', // Below the horizontal navbar
    backgroundColor: '#f3f3f3',
    borderRight: '1px solid rgba(0, 0, 0, 0.12)',
  },
}));

export default function SideMenu() {
  const [open, setOpen] = React.useState(true);

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  return (
    <Drawer
      variant="permanent"
      open={open}
      sx={{
        display: { xs: 'none', md: 'block' },
      }}
    >
      {/* Header with toggle button */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: open ? 'space-between' : 'center',
          p: 2,
          minHeight: 64,
          borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
        }}
      >
        {open && (
          <Typography
            variant="h6"
            sx={{
              fontWeight: 600,
              fontSize: '1.125rem',
              color: 'text.primary',
            }}
          >
            Menu
          </Typography>
        )}
        <IconButton
          onClick={handleDrawerToggle}
          size="small"
          sx={{
            color: 'text.secondary',
            '&:hover': {
              backgroundColor: 'rgba(0, 0, 0, 0.04)',
            },
          }}
        >
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Box>

      {/* Menu Content */}
      <Box
        sx={{
          overflow: 'auto',
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <MenuContent open={open} />
      </Box>

      {/* Footer with user info */}
      <Divider sx={{ borderColor: 'rgba(0, 0, 0, 0.12)' }} />
      <Stack
        direction="row"
        sx={{
          p: open ? 2 : 1,
          gap: 1,
          alignItems: 'center',
          justifyContent: open ? 'flex-start' : 'center',
          minHeight: 72,
          borderTop: '1px solid rgba(0, 0, 0, 0.12)',
        }}
      >
        <Avatar
          sizes="small"
          alt="Riley Carter"
          src="/static/images/avatar/7.jpg"
          sx={{ width: open ? 36 : 32, height: open ? 36 : 32 }}
        />
        {open && (
          <>
            <Box sx={{ mr: 'auto', flex: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 500, lineHeight: '16px', color: 'text.primary' }}>
                Riley Carter
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                riley@email.com
              </Typography>
            </Box>
            <OptionsMenu />
          </>
        )}
      </Stack>
    </Drawer>
  );
}
