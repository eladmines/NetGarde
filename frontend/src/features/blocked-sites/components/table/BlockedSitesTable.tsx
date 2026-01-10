import { useState, useCallback, useMemo, ChangeEvent } from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import { DataGrid, GridRowsProp, GridPaginationModel, GridSortModel } from '@mui/x-data-grid';
import { BlockedSite } from '../../types/blockedSite';
import { useBlockedSitesColumns } from './useBlockedSitesColumns';
import CircularDotsLoader from './CircularDotsLoader';
import CustomPagination from './CustomPagination';
import './BlockedSitesTable.css';

interface BlockedSitesTableProps {
  blockedSites: BlockedSite[];
  loading: boolean;
  totalCount: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  onEdit: (blockedSiteId: number) => void;
  onDelete: (blockedSite: BlockedSite) => void;
  domainSearch: string;
  onDomainSearchChange: (query: string) => void;
}

export default function BlockedSitesTable({
  blockedSites,
  loading,
  totalCount,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
  onEdit,
  onDelete,
  domainSearch,
  onDomainSearchChange,
}: BlockedSitesTableProps) {
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [sortModel, setSortModel] = useState<GridSortModel>([]);

  const handleDomainSearchChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    onDomainSearchChange(e.target.value);
  }, [onDomainSearchChange]);

  const handleCategoryChange = useCallback((categories: string[]) => {
    setSelectedCategories(categories);
  }, []);

  const allCategoryNames = useMemo(() => {
    const categorySet = new Set<string>();
    blockedSites.forEach((site) => {
      if (site.category) {
        categorySet.add(site.category);
      }
    });
    return Array.from(categorySet);
  }, [blockedSites]);

  const filteredBlockedSites = useMemo(() => {
    let filtered = blockedSites;
    if (selectedCategories.length > 0) {
      filtered = filtered.filter((blockedSite) =>
        blockedSite.category && selectedCategories.includes(blockedSite.category)
      );
    }

    return filtered;
  }, [blockedSites, selectedCategories]);

  const handlePaginationModelChange = useCallback((model: GridPaginationModel) => {
    onPageChange(model.page + 1);
    onPageSizeChange(model.pageSize);
  }, [onPageChange, onPageSizeChange]);

  const handleCustomPageChange = useCallback((newPage: number) => {
    onPageChange(newPage + 1);
  }, [onPageChange]);

  const handleSortModelChange = useCallback((newSortModel: GridSortModel) => {
    if (newSortModel.length === 0) {
      const currentSort = sortModel[0];
      if (currentSort) {
        const newDirection = currentSort.sort === 'asc' ? 'desc' : 'asc';
        setSortModel([{ field: currentSort.field, sort: newDirection }]);
      }
    } else {
      const newSort = newSortModel[0];
      if (!newSort) return;
      
      const currentSort = sortModel[0];
      
      if (currentSort && currentSort.field === newSort.field) {
        const newDirection = currentSort.sort === 'asc' ? 'desc' : 'asc';
        setSortModel([{ field: newSort.field, sort: newDirection }]);
      } else {
        setSortModel([{ field: newSort.field, sort: 'desc' }]);
      }
    }
  }, [sortModel]);

  const columns = useBlockedSitesColumns({
    onEdit,
    onDelete,
    domainSearchQuery: domainSearch,
    onDomainSearchChange: handleDomainSearchChange,
    selectedCategories,
    onCategoryChange: handleCategoryChange,
    allCategoryNames,
    sortModel,
  });

  const rows: GridRowsProp = filteredBlockedSites.map((blockedSite, index) => ({
    id: blockedSite.id,
    index: (page - 1) * pageSize + index + 1,
    domain: blockedSite.domain || '',
    reason: blockedSite.reason || '',
    category: blockedSite.category || '',
    created_at: blockedSite.created_at || null,
    updated_at: blockedSite.updated_at || null,
  }));

  return (
    <>
      {filteredBlockedSites.length === 0 && !loading && (
        <Typography variant="body2" color="text.secondary" className="emptyStateText">
          {(domainSearch || selectedCategories.length > 0)
            ? `No blocked sites found matching your filters.`
            : 'No blocked sites found. Click "Add Blocked Site" to create one.'}
        </Typography>
      )}

      <Paper className="blockedSitesTableContainer">
        {loading && (
          <Box className="loadingOverlay">
            <CircularDotsLoader />
          </Box>
        )}
        <DataGrid
          rows={rows}
          columns={columns}
          loading={loading}
          getRowId={(row) => row.id}
          className="dataGrid"
          paginationMode="server"
          rowCount={totalCount}
          paginationModel={{
            page: page - 1,
            pageSize: pageSize,
          }}
          onPaginationModelChange={handlePaginationModelChange}
          sortModel={sortModel}
          onSortModelChange={handleSortModelChange}
          pageSizeOptions={[5, 10, 25, 50]}
          disableRowSelectionOnClick
          autoHeight={true}
          columnHeaderHeight={48}
          rowHeight={40}
          disableColumnMenu
          hideFooterSelectedRowCount
          disableColumnResize
          slots={{
            pagination: () => (
              <CustomPagination
                page={page - 1}
                pageSize={pageSize}
                totalCount={totalCount}
                onPageChange={handleCustomPageChange}
              />
            ),
          }}
          onColumnHeaderClick={(params, event) => {
            const target = event.target as HTMLElement;
            
            const isDomainSearch = target.closest('.domainHeaderSearch') !== null || 
                                   target.closest('.domainHeaderContainer') !== null ||
                                   target.tagName === 'INPUT' ||
                                   target.tagName === 'TEXTAREA' ||
                                   target.closest('input') !== null ||
                                   target.closest('textarea') !== null;
            
            const isCategoryFilter = target.closest('.categoryHeaderContainer') !== null ||
                                     target.closest('.categoryFilterIcon') !== null;
            
            if (isDomainSearch || isCategoryFilter) {
              if (isDomainSearch) {
                const input = target.closest('.domainHeaderSearch')?.querySelector('input') as HTMLInputElement;
                if (input) {
                  setTimeout(() => {
                    input.focus();
                    input.select();
                  }, 0);
                }
              }
              return;
            }
            
            event.preventDefault();
            event.stopPropagation();
          }}
        />
      </Paper>
    </>
  );
}

