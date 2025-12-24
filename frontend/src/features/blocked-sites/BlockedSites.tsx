import * as React from 'react';
import Box from '@mui/material/Box';
import BlockedSitesTable from './components/table/BlockedSitesTable';
import BlockedSiteFormDialog from './components/BlockedSiteFormDialog';
import DeleteBlockedSiteDialog from './components/DeleteBlockedSiteDialog';
import BlockedSitesHeader from './components/BlockedSitesHeader';
import { useBlockedSites } from './hooks/useBlockedSites';
import { useBlockedSiteForm } from './hooks/useBlockedSiteForm';
import { useBlockedSiteActions } from './hooks/useBlockedSiteActions';

export default function BlockedSites() {
  const { blockedSites, loading, totalCount, page, pageSize, setPage, setPageSize, domainSearch, setDomainSearch, fetchBlockedSites } = useBlockedSites();
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
  } = useBlockedSiteForm(fetchBlockedSites);

  const {
    deleteDialogOpen,
    blockedSiteToDelete,
    deleting,
    handleOpenDeleteDialog,
    handleCloseDeleteDialog,
    handleConfirmDelete,
  } = useBlockedSiteActions(fetchBlockedSites);

  const handleEdit = (blockedSiteId: number) => {
    // Find in current page data
    const blockedSite = blockedSites.find((item) => item.id === blockedSiteId);
    if (!blockedSite) {
      console.warn(`Blocked site with id ${blockedSiteId} not found on current page`);
      // Could fetch by ID if not found on current page
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

