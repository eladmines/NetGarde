import { ChangeEvent } from 'react';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import { CategoryCreate } from '../types/category';
import { FORM_MODE, FormMode } from '../constants/formMode';
import PrimaryButton from '../../../shared/components/PrimaryButton';
import './CategoryFormDialog.css';

interface CategoryFormDialogProps {
  open: boolean;
  mode: FormMode;
  formData: CategoryCreate;
  submitting: boolean;
  onClose: () => void;
  onSubmit: () => void;
  onFormDataChange: (data: CategoryCreate) => void;
}

export default function CategoryFormDialog({
  open,
  mode,
  formData,
  submitting,
  onClose,
  onSubmit,
  onFormDataChange,
}: CategoryFormDialogProps) {
  const handleNameChange = (e: ChangeEvent<HTMLInputElement>) => {
    onFormDataChange({ ...formData, name: e.target.value });
  };

  const handleFormSubmit = () => {
    if (!formData.name.trim()) {
      alert('Please enter a category name');
      return;
    }
    onSubmit();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{mode === FORM_MODE.EDIT ? 'Edit Category' : 'Add New Category'}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} className="formStack">
          <TextField
            label="Name"
            fullWidth
            variant="filled"
            margin="normal"
            value={formData.name}
            onChange={handleNameChange}
            className="nameTextField"
            InputProps={{
              disableUnderline: true,
            }}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={onClose}
          variant="outlined"
          disabled={submitting}
          className="cancelButton"
        >
          Cancel
        </Button>
        <PrimaryButton onClick={handleFormSubmit} disabled={submitting}>
          {mode === FORM_MODE.EDIT ? 'Save Changes' : 'Add Category'}
        </PrimaryButton>
      </DialogActions>
    </Dialog>
  );
}

