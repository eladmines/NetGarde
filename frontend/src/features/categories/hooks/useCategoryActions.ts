import * as React from 'react';
import { Category } from '../types/category';
import { API_ENDPOINTS } from '../config/api';

export function useCategoryActions(onDeleteSuccess?: () => void) {
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [categoryToDelete, setCategoryToDelete] = React.useState<Category | null>(null);
  const [deleting, setDeleting] = React.useState(false);

  const handleOpenDeleteDialog = React.useCallback((category: Category) => {
    setCategoryToDelete(category);
    setDeleteDialogOpen(true);
  }, []);

  const handleCloseDeleteDialog = React.useCallback(() => {
    if (!deleting) {
      setDeleteDialogOpen(false);
      setCategoryToDelete(null);
    }
  }, [deleting]);

  const handleConfirmDelete = React.useCallback(async () => {
    if (!categoryToDelete) return;

    try {
      setDeleting(true);
      const response = await fetch(API_ENDPOINTS.category(categoryToDelete.id), {
        method: 'DELETE',
      });

      if (response.ok) {
        setDeleteDialogOpen(false);
        setCategoryToDelete(null);
        onDeleteSuccess?.();
      } else {
        console.error('Error deleting category');
      }
    } catch (error) {
      console.error('Error deleting category:', error);
    } finally {
      setDeleting(false);
    }
  }, [categoryToDelete, onDeleteSuccess]);

  return {
    deleteDialogOpen,
    categoryToDelete,
    deleting,
    handleOpenDeleteDialog,
    handleCloseDeleteDialog,
    handleConfirmDelete,
  };
}

