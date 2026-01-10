import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import AddIcon from '@mui/icons-material/Add';
import PrimaryButton from '../../../shared/components/PrimaryButton';
import './CategoriesHeader.css';

interface CategoriesHeaderProps {
  onAddClick: () => void;
}

export default function CategoriesHeader({ onAddClick }: CategoriesHeaderProps) {
  return (
    <Stack
      direction="row"
      justifyContent="space-between"
      alignItems="center"
      className="headerStack"
    >
      <Typography component="h1" variant="h4">
        Categories
      </Typography>

      <PrimaryButton onClick={onAddClick} startIcon={<AddIcon />}>
        Add Category
      </PrimaryButton>
    </Stack>
  );
}

