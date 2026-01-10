import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PrimaryButton from '../../../shared/components/PrimaryButton';
import { Category } from '../types/category';
import { formatDate } from '../../../shared/utils/dateUtils';

interface CategoryDetailsDialogProps {
  open: boolean;
  category: Category | null;
  blockedSitesCount?: number;
  onClose: () => void;
  onEdit: (categoryId: number) => void;
  onDelete: (category: Category) => void;
}

export default function CategoryDetailsDialog({
  open,
  category,
  blockedSitesCount = 0,
  onClose,
  onEdit,
  onDelete,
}: CategoryDetailsDialogProps) {
  if (!category) {
    return null;
  }

  const handleEdit = () => {
    onEdit(category.id);
    onClose();
  };

  const handleDelete = () => {
    onDelete(category);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Category Details</DialogTitle>
      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              Name
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {category.name}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              Blocked Sites
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {blockedSitesCount}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              Created
            </Typography>
            <Typography variant="body2">
              {category.created_at ? formatDate(category.created_at) : 'N/A'}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              Last Updated
            </Typography>
            <Typography variant="body2">
              {category.updated_at ? formatDate(category.updated_at) : 'N/A'}
            </Typography>
          </Box>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={handleDelete}
          variant="outlined"
          color="error"
          startIcon={<DeleteIcon />}
          sx={{ mr: 'auto' }}
        >
          Delete
        </Button>
        <Button onClick={onClose} variant="outlined">
          Close
        </Button>
        <PrimaryButton onClick={handleEdit} startIcon={<EditIcon />}>
          Edit
        </PrimaryButton>
      </DialogActions>
    </Dialog>
  );
}

