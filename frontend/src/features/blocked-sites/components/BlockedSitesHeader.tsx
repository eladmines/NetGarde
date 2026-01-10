import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import AddIcon from '@mui/icons-material/Add';
import PrimaryButton from '../../../shared/components/PrimaryButton';
import './BlockedSitesHeader.css';

interface BlockedSitesHeaderProps {
  onAddClick: () => void;
}

export default function BlockedSitesHeader({ onAddClick }: BlockedSitesHeaderProps) {
  return (
    <Stack
      direction="row"
      justifyContent="space-between"
      alignItems="center"
      className="headerStack"
    >
      <Typography 
        component="h1" 
        variant="h5"
        sx={{ 
          fontWeight: 600,
          color: 'text.primary',
          lineHeight: 1.2,
        }}
      >
        Blocked Sites
      </Typography>

      <PrimaryButton onClick={onAddClick} startIcon={<AddIcon />}>
        Add Blocked Site
      </PrimaryButton>
    </Stack>
  );
}

