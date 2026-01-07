import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import EditRoundedIcon from '@mui/icons-material/EditRounded';
import DeleteOutlineRoundedIcon from '@mui/icons-material/DeleteOutlineRounded';
import { Category } from '../../types/category';

interface CategoriesActionsCellProps {
  category: Category;
  onEdit: (categoryId: number) => void;
  onDelete: (category: Category) => void;
}

export default function CategoriesActionsCell({
  category,
  onEdit,
  onDelete,
}: CategoriesActionsCellProps) {
  return (
    <Stack direction="row" spacing={0.5}>
      <Tooltip title="Edit category">
        <IconButton
          size="small"
          aria-label={`Edit ${category.name}`}
          onClick={() => onEdit(category.id)}
        >
          <EditRoundedIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <Tooltip title="Delete category">
        <IconButton
          size="small"
          color="error"
          aria-label={`Delete ${category.name}`}
          onClick={() => onDelete(category)}
        >
          <DeleteOutlineRoundedIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </Stack>
  );
}

