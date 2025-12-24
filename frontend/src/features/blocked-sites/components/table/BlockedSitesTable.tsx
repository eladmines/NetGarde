import * as React from 'react';
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
  const [selectedCategories, setSelectedCategories] = React.useState<string[]>([]);
  const [sortModel, setSortModel] = React.useState<GridSortModel>([]);

  const handleDomainSearchChange = React.useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onDomainSearchChange(e.target.value);
  }, [onDomainSearchChange]);

  const handleCategoryChange = React.useCallback((categories: string[]) => {
    setSelectedCategories(categories);
  }, []);

  // Extract all unique category names from blocked sites
  const allCategoryNames = React.useMemo(() => {
    const categorySet = new Set<string>();
    blockedSites.forEach((site) => {
      if (site.category) {
        categorySet.add(site.category);
      }
    });
    return Array.from(categorySet);
  }, [blockedSites]);

  // Filter by selected categories (client-side on current page)
  // Note: Domain search is now handled server-side
  const filteredBlockedSites = React.useMemo(() => {
    let filtered = blockedSites;

    // Filter by selected categories (client-side on current page)
    if (selectedCategories.length > 0) {
      filtered = filtered.filter((blockedSite) =>
        blockedSite.category && selectedCategories.includes(blockedSite.category)
      );
    }

    return filtered;
  }, [blockedSites, selectedCategories]);

  const handlePaginationModelChange = React.useCallback((model: GridPaginationModel) => {
    onPageChange(model.page + 1); // DataGrid uses 0-based, API uses 1-based
    onPageSizeChange(model.pageSize);
  }, [onPageChange, onPageSizeChange]);

  const handleCustomPageChange = React.useCallback((newPage: number) => {
    onPageChange(newPage + 1); // CustomPagination uses 0-based, API uses 1-based
  }, [onPageChange]);

  // Handle sort model change - only allow asc and desc, no unsorted state
  // Only one column can be sorted at a time
  const handleSortModelChange = React.useCallback((newSortModel: GridSortModel) => {
    if (newSortModel.length === 0) {
      // If trying to clear sort, keep the current sort but toggle direction
      const currentSort = sortModel[0];
      if (currentSort) {
        const newDirection = currentSort.sort === 'asc' ? 'desc' : 'asc';
        setSortModel([{ field: currentSort.field, sort: newDirection }]);
      }
      // If no current sort, do nothing (both arrows stay at 0.5 opacity)
    } else {
      // Only take the first sort (single column sorting)
      const newSort = newSortModel[0];
      const currentSort = sortModel[0];
      
      if (currentSort && currentSort.field === newSort.field) {
        // Same column: toggle direction between asc and desc
        const newDirection = currentSort.sort === 'asc' ? 'desc' : 'asc';
        setSortModel([{ field: newSort.field, sort: newDirection }]);
      } else {
        // Different column: switch to new column with desc as default
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
    id: blockedSite.id, // Keep real ID for internal use (getRowId)
    index: (page - 1) * pageSize + index + 1, // Calculate index based on server pagination
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
            page: page - 1, // DataGrid uses 0-based, API uses 1-based
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
            // Only prevent default if clicking on the header itself, not on interactive elements
            const target = event.target as HTMLElement;
            
            // Check if click is on domain search input or container
            const isDomainSearch = target.closest('.domainHeaderSearch') !== null || 
                                   target.closest('.domainHeaderContainer') !== null ||
                                   target.tagName === 'INPUT' ||
                                   target.tagName === 'TEXTAREA' ||
                                   target.closest('input') !== null ||
                                   target.closest('textarea') !== null;
            
            // Check if click is on category filter
            const isCategoryFilter = target.closest('.categoryHeaderContainer') !== null ||
                                     target.closest('.categoryFilterIcon') !== null;
            
            // Only prevent header click behavior if NOT clicking on interactive elements
            if (isDomainSearch || isCategoryFilter) {
              // For interactive elements, manually focus the input if it's the search
              if (isDomainSearch) {
                const input = target.closest('.domainHeaderSearch')?.querySelector('input') as HTMLInputElement;
                if (input) {
                  setTimeout(() => {
                    input.focus();
                    input.select(); // Select text if any for easier editing
                  }, 0);
                }
              }
              // Don't prevent default or stop propagation - let the click proceed
              return;
            }
            
            // For non-interactive header areas, prevent default behavior
            event.preventDefault();
            event.stopPropagation();
          }}
        />
      </Paper>
    </>
  );
}

