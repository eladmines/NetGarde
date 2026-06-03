import Stack from '@mui/material/Stack';
import NavbarBreadcrumbs from './NavbarBreadcrumbs';

export default function Header() {
  return (
    <Stack
      direction="row"
      sx={{
        display: { xs: 'none', md: 'flex' },
        width: '100%',
        alignItems: 'center',
        justifyContent: 'flex-start',
        height: { xs: '56px', md: '48px' },
        px: 2,
        backgroundColor: 'background.paper',
        borderBottom: 1,
        borderColor: 'divider',
        borderRadius: '0',
      }}
      spacing={0}
    >
      <NavbarBreadcrumbs />
    </Stack>
  );
}
