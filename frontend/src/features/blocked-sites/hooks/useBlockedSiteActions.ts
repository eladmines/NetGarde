import { useState, useCallback } from 'react';
import { BlockedSite } from '../types/blockedSite';
import { API_ENDPOINTS } from '../config/api';

export function useBlockedSiteActions(onDeleteSuccess?: () => void) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [blockedSiteToDelete, setBlockedSiteToDelete] = useState<BlockedSite | null>(null);
  const [deleting, setDeleting] = useState(false);

  const handleOpenDeleteDialog = useCallback((blockedSite: BlockedSite) => {
    setBlockedSiteToDelete(blockedSite);
    setDeleteDialogOpen(true);
  }, []);

  const handleCloseDeleteDialog = useCallback(() => {
    if (!deleting) {
      setDeleteDialogOpen(false);
      setBlockedSiteToDelete(null);
    }
  }, [deleting]);

  const handleConfirmDelete = useCallback(async () => {
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

