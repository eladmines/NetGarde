import { useEffect, ChangeEvent } from 'react';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import { SelectChangeEvent } from '@mui/material/Select';
import { BlockedSiteCreate } from '../types/blockedSite';
import { FORM_MODE, FormMode } from '../constants/formMode';
import { useCategories } from '../../categories/hooks/useCategories';
import PrimaryButton from '../../../shared/components/PrimaryButton';
import './BlockedSiteFormDialog.css';

interface BlockedSiteFormDialogProps {
  open: boolean;
  mode: FormMode;
  formData: BlockedSiteCreate;
  submitting: boolean;
  onClose: () => void;
  onSubmit: () => void;
  onFormDataChange: (data: BlockedSiteCreate) => void;
}

export default function BlockedSiteFormDialog({
  open,
  mode,
  formData,
  submitting,
  onClose,
  onSubmit,
  onFormDataChange,
}: BlockedSiteFormDialogProps) {
  const { categories, loading: categoriesLoading, fetchCategories } = useCategories();

  useEffect(() => {
    if (open) {
      fetchCategories();
    }
  }, [open, fetchCategories]);

  const handleDomainChange = (e: ChangeEvent<HTMLInputElement>) => {
    onFormDataChange({ ...formData, domain: e.target.value });
  };

  const handleReasonChange = (e: ChangeEvent<HTMLInputElement>) => {
    onFormDataChange({ ...formData, reason: e.target.value });
  };

  const handleCategoryChange = (e: SelectChangeEvent<string>) => {
    const selectedCategoryName = e.target.value;
    onFormDataChange({ ...formData, category: selectedCategoryName === '' ? null : selectedCategoryName });
  };

  const handleFormSubmit = () => {
    if (!formData.domain.trim()) {
      alert('Please enter a domain');
      return;
    }
    if (!formData.reason.trim()) {
      alert('Please enter a reason');
      return;
    }
    onSubmit();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{mode === FORM_MODE.EDIT ? 'Edit Blocked Site' : 'Add New Blocked Site'}</DialogTitle>
      <DialogContent>
      <Stack spacing={2} className="formStack">
  <TextField
    label="Domain"
    fullWidth
    variant="filled"
    margin="normal"
    value={formData.domain}
    onChange={handleDomainChange}
    className="domainTextField"
    InputProps={{
      disableUnderline: true,
    }}
  />

<FormControl fullWidth variant="filled" margin="normal" className="categoryFormControl">
  <InputLabel id="category-select-label">Category</InputLabel>
  <Select
    labelId="category-select-label"
    id="category-select"
    value={formData.category || ''}
    onChange={handleCategoryChange}
    label="Category"
    className="categorySelect"
    disabled={categoriesLoading}
  >
    <MenuItem value="">
      <em>None</em>
    </MenuItem>
    {categories.map((category) => (
      <MenuItem key={category.id} value={category.name}>
        {category.name}
      </MenuItem>
    ))}
  </Select>
</FormControl>

<TextField
  label="Reason"
  fullWidth
  multiline
  rows={4}
  value={formData.reason}
  onChange={handleReasonChange}
  variant="filled"
  margin="normal"
  className="reasonTextField"
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
          {mode === FORM_MODE.EDIT ? 'Save Changes' : 'Add Blocked Site'}
        </PrimaryButton>
      </DialogActions>
    </Dialog>
  );
}

