import * as React from 'react';
import { BlockedSite } from '../types/blockedSite';
import { API_ENDPOINTS } from '../config/api';

export function useBlockedSiteActions(onDeleteSuccess?: () => void) {
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [blockedSiteToDelete, setBlockedSiteToDelete] = React.useState<BlockedSite | null>(null);
  const [deleting, setDeleting] = React.useState(false);

  const handleOpenDeleteDialog = React.useCallback((blockedSite: BlockedSite) => {
    setBlockedSiteToDelete(blockedSite);
    setDeleteDialogOpen(true);
  }, []);

  const handleCloseDeleteDialog = React.useCallback(() => {
    if (!deleting) {
      setDeleteDialogOpen(false);
      setBlockedSiteToDelete(null);
    }
  }, [deleting]);

  const handleConfirmDelete = React.useCallback(async () => {
    if (!blockedSiteToDelete) return;

    try {
      setDeleting(true);
      const response = await fetch(API_ENDPOINTS.blockedSite(blockedSiteToDelete.id), {
        method: 'DELETE',
      });

      if (response.ok) {
        setDeleteDialogOpen(false);
        setBlockedSiteToDelete(null);
        onDeleteSuccess?.(); // Refresh the list
      } else {
        console.error('Error deleting blocked site');
      }
    } catch (error) {
      console.error('Error deleting blocked site:', error);
    } finally {
      setDeleting(false);
    }
  }, [blockedSiteToDelete, onDeleteSuccess]);

  return {
    deleteDialogOpen,
    blockedSiteToDelete,
    deleting,
    handleOpenDeleteDialog,
    handleCloseDeleteDialog,
    handleConfirmDelete,
  };
}

