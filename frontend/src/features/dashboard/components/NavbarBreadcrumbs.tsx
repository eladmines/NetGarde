import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Breadcrumbs, { breadcrumbsClasses } from '@mui/material/Breadcrumbs';
import NavigateNextRoundedIcon from '@mui/icons-material/NavigateNextRounded';

const StyledBreadcrumbs = styled(Breadcrumbs)(({ theme }) => ({
  margin: 0,
  [`& .${breadcrumbsClasses.separator}`]: {
    color: (theme.vars || theme).palette.action.disabled,
    margin: 1,
  },
  [`& .${breadcrumbsClasses.ol}`]: {
    alignItems: 'center',
    lineHeight: 0.9,
  },
  [`& .${breadcrumbsClasses.li}`]: {
    lineHeight: 0.9,
  },
}));

export default function NavbarBreadcrumbs() {
  return (
    <StyledBreadcrumbs
      aria-label="breadcrumb"
      separator={<NavigateNextRoundedIcon fontSize="small" />}
    >
      <Typography variant="body1" sx={{ lineHeight: 0.9 }}>Dashboard</Typography>
      <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 600, lineHeight: 0.9 }}>
        Home
      </Typography>
    </StyledBreadcrumbs>
  );
}
