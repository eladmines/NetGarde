import { useMemo } from 'react';
import { GridColDef } from '@mui/x-data-grid';
import { Category } from '../../types/category';
import { formatDate } from '../../../../shared/utils/dateUtils';
import CategoriesActionsCell from './CategoriesActionsCell';

interface UseCategoriesColumnsProps {
  onEdit: (categoryId: number) => void;
  onDelete: (category: Category) => void;
  blockedSitesCounts: Record<string, number>;
}

export function useCategoriesColumns({
  onEdit,
  onDelete,
  blockedSitesCounts,
}: UseCategoriesColumnsProps): GridColDef[] {
  return useMemo<GridColDef[]>(
    () => [
      {
        field: 'id',
        headerName: 'ID',
        width: 70,
        resizable: false,
      },
      {
        field: 'name',
        headerName: 'Name',
        flex: 1,
        minWidth: 150,
        resizable: false,
      },
      {
        field: 'blocked_sites_count',
        headerName: 'Blocked Sites',
        width: 150,
        resizable: false,
        align: 'center',
        headerAlign: 'center',
        renderCell: (params) => {
          return params.value || 0;
        },
      },
      {
        field: 'created_at',
        headerName: 'Created',
        width: 180,
        resizable: false,
        renderCell: (params) => {
          return formatDate(params.value);
        },
      },
      {
        field: 'updated_at',
        headerName: 'Updated',
        width: 180,
        resizable: false,
        renderCell: (params) => {
          return formatDate(params.value);
        },
      },
      {
        field: 'actions',
        headerName: 'Actions',
        width: 120,
        resizable: false,
        sortable: false,
        filterable: false,
        disableColumnMenu: true,
        renderCell: (params) => {
          const category = params.row as Category;
          return (
            <CategoriesActionsCell
              category={category}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          );
        },
      },
    ],
    [onEdit, onDelete, blockedSitesCounts],
  );
}

