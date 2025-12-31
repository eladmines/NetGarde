import * as React from 'react';
import { BlockedSite, BlockedSiteCreate } from '../types/blockedSite';
import { API_ENDPOINTS } from '../config/api';
import { FORM_MODE, FormMode } from '../constants/formMode';

export function useBlockedSiteForm(onSuccess?: () => void) {
  const [openDialog, setOpenDialog] = React.useState(false);
  const [dialogMode, setDialogMode] = React.useState<FormMode>(FORM_MODE.CREATE);
  const [formData, setFormData] = React.useState<BlockedSiteCreate>({ domain: '', reason: '', category: null });
  const [editingBlockedSite, setEditingBlockedSite] = React.useState<BlockedSite | null>(null);
  const [submitting, setSubmitting] = React.useState(false);

  const resetForm = React.useCallback(() => {
    setFormData({ domain: '', reason: '', category: null });
  }, []);

  const handleOpenCreateDialog = React.useCallback(() => {
    setDialogMode(FORM_MODE.CREATE);
    setEditingBlockedSite(null);
    resetForm();
    setOpenDialog(true);
  }, [resetForm]);

  const handleOpenEditDialog = React.useCallback((blockedSite: BlockedSite) => {
    console.log('Editing blocked site:', blockedSite);
    setDialogMode(FORM_MODE.EDIT);
    setEditingBlockedSite(blockedSite);
    setFormData({
      domain: blockedSite.domain ?? '',
      reason: blockedSite.reason ?? '',
      category: blockedSite.category ?? null,
    });
    setOpenDialog(true);
  }, []);

  const handleCloseDialog = React.useCallback(() => {
    setOpenDialog(false);
    resetForm();
    setEditingBlockedSite(null);
    setDialogMode(FORM_MODE.CREATE);
  }, [resetForm]);

  const handleSubmit = React.useCallback(async () => {
    const isEdit = dialogMode === FORM_MODE.EDIT && editingBlockedSite;
    try {
      setSubmitting(true);
      
      // Clean the form data: ensure category is null if empty string
      const cleanedFormData = {
        ...formData,
        category: formData.category === '' || formData.category === null ? null : formData.category,
      };
      
      const response = await fetch(
        isEdit ? API_ENDPOINTS.blockedSite(editingBlockedSite.id) : API_ENDPOINTS.blockedSites(),
        {
          method: isEdit ? 'PUT' : 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(cleanedFormData),
        }
      );

      if (response.ok) {
        handleCloseDialog();
        onSuccess?.(); // Refresh the list
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error(isEdit ? 'Error updating blocked site' : 'Error creating blocked site', errorData);
        alert(errorData.detail || (isEdit ? 'Failed to update blocked site' : 'Failed to create blocked site'));
      }
    } catch (error) {
      console.error(isEdit ? 'Error updating blocked site:' : 'Error creating blocked site:', error);
      alert(isEdit ? 'Failed to update blocked site. Please try again.' : 'Failed to create blocked site. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }, [dialogMode, editingBlockedSite, formData, handleCloseDialog, onSuccess]);

  return {
    openDialog,
    dialogMode,
    formData,
    editingBlockedSite,
    submitting,
    setFormData,
    handleOpenCreateDialog,
    handleOpenEditDialog,
    handleCloseDialog,
    handleSubmit,
  };
}

