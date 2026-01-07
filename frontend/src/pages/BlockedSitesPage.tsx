import { useCallback } from 'react';
import Box from '@mui/material/Box';
import BlockedSitesTable from '../features/blocked-sites/components/table/BlockedSitesTable';
import BlockedSiteFormDialog from '../features/blocked-sites/components/BlockedSiteFormDialog';
import DeleteBlockedSiteDialog from '../features/blocked-sites/components/DeleteBlockedSiteDialog';
import BlockedSitesHeader from '../features/blocked-sites/components/BlockedSitesHeader';
import { useBlockedSites } from '../features/blocked-sites/hooks/useBlockedSites';
import { useBlockedSiteForm } from '../features/blocked-sites/hooks/useBlockedSiteForm';
import { useBlockedSiteActions } from '../features/blocked-sites/hooks/useBlockedSiteActions';

export default function BlockedSitesPage() {
  const { blockedSites, loading, totalCount, page, pageSize, setPage, setPageSize, domainSearch, setDomainSearch, fetchBlockedSites } = useBlockedSites();
  
  const refreshBlockedSites = useCallback(() => {
    fetchBlockedSites(page, pageSize, domainSearch);
  }, [fetchBlockedSites, page, pageSize, domainSearch]);
  
  const {
    openDialog,
    dialogMode,
    formData,
    submitting,
    setFormData,
    handleOpenCreateDialog,
    handleOpenEditDialog,
    handleCloseDialog,
    handleSubmit,
  } = useBlockedSiteForm(refreshBlockedSites);

  const {
    deleteDialogOpen,
    blockedSiteToDelete,
    deleting,
    handleOpenDeleteDialog,
    handleCloseDeleteDialog,
    handleConfirmDelete,
  } = useBlockedSiteActions(refreshBlockedSites);

  const handleEdit = (blockedSiteId: number) => {
    const blockedSite = blockedSites.find((item) => item.id === blockedSiteId);
    if (!blockedSite) {
      console.warn(`Blocked site with id ${blockedSiteId} not found on current page`);
      return;
    }
    handleOpenEditDialog(blockedSite);
  };

  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
      <BlockedSitesHeader onAddClick={handleOpenCreateDialog} />

      <BlockedSitesTable
        blockedSites={blockedSites}
        loading={loading}
        totalCount={totalCount}
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
        onPageSizeChange={setPageSize}
        onEdit={handleEdit}
        onDelete={handleOpenDeleteDialog}
        domainSearch={domainSearch}
        onDomainSearchChange={setDomainSearch}
      />

      <BlockedSiteFormDialog
        open={openDialog}
        mode={dialogMode}
        formData={formData}
        submitting={submitting}
        onClose={handleCloseDialog}
        onSubmit={handleSubmit}
        onFormDataChange={setFormData}
      />

      <DeleteBlockedSiteDialog
        open={deleteDialogOpen}
        blockedSite={blockedSiteToDelete}
        onClose={handleCloseDeleteDialog}
        onConfirm={handleConfirmDelete}
        deleting={deleting}
      />
    </Box>
  );
}

