import { ReactNode } from 'react';
import type {} from '@mui/x-date-pickers/themeAugmentation';
import type {} from '@mui/x-charts/themeAugmentation';
import type {} from '@mui/x-data-grid/themeAugmentation';
import type {} from '@mui/x-tree-view/themeAugmentation';
import { alpha } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import AppNavbar from '../../features/dashboard/components/AppNavbar';
import Header from '../../features/dashboard/components/Header';
import SideMenu from '../../features/dashboard/components/SideMenu';
import AppTheme from '../theme/AppTheme';
import {
  chartsCustomizations,
  datePickersCustomizations,
  treeViewCustomizations,
} from '../../features/dashboard/theme/customizations';

const xThemeComponents = {
  ...chartsCustomizations,
  ...datePickersCustomizations,
  ...treeViewCustomizations,
};

interface LayoutProps {
  children: ReactNode;
  disableCustomTheme?: boolean;
}

export default function Layout({ children, disableCustomTheme }: LayoutProps) {
  return (
    <AppTheme disableCustomTheme={disableCustomTheme} themeComponents={xThemeComponents}>
      <CssBaseline enableColorScheme />
      <Box sx={{ display: 'flex' }}>
        <SideMenu />
        <AppNavbar />
        <Box
          component="main"
          sx={(theme) => ({
            flexGrow: 1,
            backgroundColor: theme.vars
              ? `rgba(${theme.vars.palette.background.defaultChannel} / 1)`
              : alpha(theme.palette.background.default, 1),
            overflow: 'auto',
          })}
        >
          <Stack
            spacing={2}
            sx={{
              alignItems: 'center',
              mx: 3,
              pb: 5,
              mt: { xs: 8, md: 0 },
            }}
          >
            <Header />
            {children}
          </Stack>
        </Box>
      </Box>
    </AppTheme>
  );
}

