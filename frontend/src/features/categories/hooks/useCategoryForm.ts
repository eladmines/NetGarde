import { useState, useCallback } from 'react';
import { Category, CategoryCreate } from '../types/category';
import { API_ENDPOINTS } from '../config/api';
import { FORM_MODE, FormMode } from '../constants/formMode';

export function useCategoryForm(onSuccess?: () => void) {
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState<FormMode>(FORM_MODE.CREATE);
  const [formData, setFormData] = useState<CategoryCreate>({ name: '', created_by: null, updated_by: null });
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const resetForm = useCallback(() => {
    setFormData({ name: '', created_by: null, updated_by: null });
  }, []);

  const handleOpenCreateDialog = useCallback(() => {
    setDialogMode(FORM_MODE.CREATE);
    setEditingCategory(null);
    resetForm();
    setOpenDialog(true);
  }, [resetForm]);

  const handleOpenEditDialog = useCallback((category: Category) => {
    setDialogMode(FORM_MODE.EDIT);
    setEditingCategory(category);
    setFormData({
      name: category.name ?? '',
      created_by: category.created_by ?? null,
      updated_by: category.updated_by ?? null,
    });
    setOpenDialog(true);
  }, []);

  const handleCloseDialog = useCallback(() => {
    setOpenDialog(false);
    resetForm();
    setEditingCategory(null);
    setDialogMode(FORM_MODE.CREATE);
  }, [resetForm]);

  const handleSubmit = useCallback(async () => {
    const isEdit = dialogMode === FORM_MODE.EDIT && editingCategory;
    try {
      setSubmitting(true);
      const response = await fetch(
        isEdit ? API_ENDPOINTS.category(editingCategory.id) : API_ENDPOINTS.categories,
        {
          method: isEdit ? 'PUT' : 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        }
      );

      if (response.ok) {
        handleCloseDialog();
        onSuccess?.();
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error(isEdit ? 'Error updating category' : 'Error creating category', errorData);
        alert(errorData.detail || (isEdit ? 'Failed to update category' : 'Failed to create category'));
      }
    } catch (error) {
      console.error(isEdit ? 'Error updating category:' : 'Error creating category:', error);
      alert(isEdit ? 'Failed to update category. Please try again.' : 'Failed to create category. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }, [dialogMode, editingCategory, formData, handleCloseDialog, onSuccess]);

  return {
    openDialog,
    dialogMode,
    formData,
    editingCategory,
    submitting,
    setFormData,
    handleOpenCreateDialog,
    handleOpenEditDialog,
    handleCloseDialog,
    handleSubmit,
  };
}

