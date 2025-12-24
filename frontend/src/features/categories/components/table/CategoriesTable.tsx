import * as React from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import { DataGrid, GridRowsProp } from '@mui/x-data-grid';
import { Category } from '../../types/category';
import { useCategoriesColumns } from './useCategoriesColumns';
import { API_ENDPOINTS } from '../../../blocked-sites/config/api';
import './CategoriesTable.css';

interface CategoriesTableProps {
  categories: Category[];
  loading: boolean;
  onEdit: (categoryId: number) => void;
  onDelete: (category: Category) => void;
}

interface CategoryCountsResponse {
  counts: Record<string, number>;
}

export default function CategoriesTable({
  categories,
  loading,
  onEdit,
  onDelete,
}: CategoriesTableProps) {
  const [blockedSitesCounts, setBlockedSitesCounts] = React.useState<Record<string, number>>({});
  const [loadingCounts, setLoadingCounts] = React.useState(true);

  // Fetch blocked sites counts by category from the API
  React.useEffect(() => {
    const fetchBlockedSitesCounts = async () => {
      try {
        setLoadingCounts(true);
        const response = await fetch(API_ENDPOINTS.blockedSitesCountsByCategory());
        if (response.ok) {
          const data: CategoryCountsResponse = await response.json();
          if (data.counts) {
            setBlockedSitesCounts(data.counts);
          }
        } else {
          console.error('Failed to fetch blocked sites counts:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('Error fetching blocked sites counts:', error);
      } finally {
        setLoadingCounts(false);
      }
    };

    fetchBlockedSitesCounts();
  }, []);

  const columns = useCategoriesColumns({ onEdit, onDelete, blockedSitesCounts });
  const rows: GridRowsProp = categories.map((category) => ({
    id: category.id,
    name: category.name || '',
    blocked_sites_count: blockedSitesCounts[category.name || ''] || 0,
    created_at: category.created_at || null,
    updated_at: category.updated_at || null,
  }));

  return (
    <>
      {categories.length === 0 && !loading && (
        <Typography variant="body2" color="text.secondary" className="emptyStateText">
          No categories found. Click "Add Category" to create one.
        </Typography>
      )}

      {categories.length > 0 && (
        <Typography variant="body2" color="text.secondary" className="emptyStateText">
          Found {categories.length} categor{categories.length === 1 ? 'y' : 'ies'}
        </Typography>
      )}

      <Paper className="categoriesTableContainer">
        <DataGrid
          rows={rows}
          columns={columns}
          loading={loading}
          getRowId={(row) => row.id}
          className="dataGrid"
          initialState={{
            pagination: {
              paginationModel: { page: 0, pageSize: 10 },
            },
          }}
          pageSizeOptions={[5, 10, 25, 50]}
          disableRowSelectionOnClick
          autoHeight={false}
          columnHeaderHeight={48}
          rowHeight={40}
          disableColumnMenu
          hideFooterSelectedRowCount
          disableColumnResize
        />
      </Paper>
    </>
  );
}

