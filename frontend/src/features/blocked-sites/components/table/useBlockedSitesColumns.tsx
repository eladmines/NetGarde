import { useMemo, ChangeEvent } from 'react';
import { GridColDef, GridSortModel } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
import InputAdornment from '@mui/material/InputAdornment';
import OutlinedInput from '@mui/material/OutlinedInput';
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import { BlockedSite } from '../../types/blockedSite';
import { formatDate } from '../../../../shared/utils/dateUtils';
import BlockedSitesActionsCell from './BlockedSitesActionsCell';
import CategoryFilter from './CategoryFilter';
import './useBlockedSitesColumns.css';

interface UseBlockedSitesColumnsProps {
  onEdit: (blockedSiteId: number) => void;
  onDelete: (blockedSite: BlockedSite) => void;
  domainSearchQuery: string;
  onDomainSearchChange: (e: ChangeEvent<HTMLInputElement>) => void;
  selectedCategories: string[];
  onCategoryChange: (categories: string[]) => void;
  allCategoryNames: string[];
  sortModel: GridSortModel;
}

export function useBlockedSitesColumns({
  onEdit,
  onDelete,
  domainSearchQuery,
  onDomainSearchChange,
  selectedCategories,
  onCategoryChange,
  allCategoryNames,
  sortModel,
}: UseBlockedSitesColumnsProps): GridColDef[] {
  return useMemo<GridColDef[]>(
    () => [
      {
        field: 'index',
        headerName: '#',
        width: 70,
        resizable: false,
        sortable: false,
        renderCell: (params) => params.value || params.row.index || '',
      },
      {
        field: 'domain',
        headerName: 'Domain',
        flex: 1,
        minWidth: 150,
        resizable: false,
        sortable: false,
        renderHeader: () => (
          <Box className="domainHeaderContainer">
            <Typography variant="body2" className="domainHeaderTitle">
              Domain
            </Typography>
            <OutlinedInput
              size="small"
              placeholder="Search…"
              className="domainHeaderSearch"
              value={domainSearchQuery}
              onChange={onDomainSearchChange}
              onClick={(e) => {
                e.stopPropagation();
                const input = (e.currentTarget as HTMLElement).querySelector('input') as HTMLInputElement;
                if (input) {
                  input.focus();
                }
              }}
              onMouseDown={(e) => {
                e.stopPropagation();
                if ((e.target as HTMLElement).tagName !== 'INPUT') {
                  const input = (e.currentTarget as HTMLElement).querySelector('input') as HTMLInputElement;
                  if (input) {
                    e.preventDefault();
                    input.focus();
                  }
                }
              }}
              startAdornment={
                <InputAdornment position="start" className="domainHeaderAdornment">
                  <SearchRoundedIcon fontSize="small" />
                </InputAdornment>
              }
              inputProps={{
                'aria-label': 'search domain',
              }}
            />
          </Box>
        ),
      },
      {
        field: 'reason',
        headerName: 'Reason',
        flex: 1,
        minWidth: 150,
        resizable: false,
        sortable: false,
        renderCell: (params) => {
          const reason = params.value || '';
          const isLong = reason.length > 50;
          
          return (
            <Tooltip title={isLong ? reason : ''} arrow placement="top">
              <Box
                sx={{
                  width: '100%',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  cursor: isLong ? 'help' : 'default',
                }}
              >
                {reason}
              </Box>
            </Tooltip>
          );
        },
      },
      {
        field: 'category',
        headerName: 'Category',
        width: 150,
        resizable: false,
        sortable: false,
        renderHeader: () => (
          <Box className="categoryHeaderContainer">
            <Typography variant="body2" className="categoryHeaderTitle">
              Category
            </Typography>
            <Box className="categoryFilterWrapper">
              <CategoryFilter
                selectedCategories={selectedCategories}
                onCategoryChange={onCategoryChange}
                allCategoryNames={allCategoryNames}
              />
            </Box>
          </Box>
        ),
      },
      {
        field: 'created_at',
        headerName: 'Created',
        width: 180,
        resizable: false,
        renderHeader: () => {
          const currentSort = sortModel.find((s) => s.field === 'created_at');
          const isSorted = !!currentSort;
          const sortDirection = currentSort?.sort || 'desc';
          const opacity = isSorted ? 1 : 0.5;
          
          return (
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', paddingRight: 0 }}>
              <Typography variant="body2" sx={{ color: 'rgba(0, 0, 0, 0.87)', marginRight: 'auto', fontWeight: 600 }}>
                Created
              </Typography>
              <IconButton
                size="small"
                className="sortArrowButton"
                sx={{
                  opacity: opacity,
                  color: 'rgba(0, 0, 0, 0.6)',
                  padding: '4px',
                  backgroundColor: 'transparent',
                  border: 'none',
                  marginLeft: 'auto',
                  marginRight: '-8px',
                  transition: 'opacity 0.2s ease',
                  '&:hover': { opacity: 1, backgroundColor: 'transparent', color: 'rgba(0, 0, 0, 0.87)' },
                }}
              >
                {sortDirection === 'asc' ? (
                  <ArrowUpwardIcon fontSize="small" />
                ) : (
                  <ArrowDownwardIcon fontSize="small" />
                )}
              </IconButton>
            </Box>
          );
        },
        renderCell: (params) => {
          return formatDate(params.value);
        },
      },
      {
        field: 'updated_at',
        headerName: 'Updated',
        width: 180,
        resizable: false,
        renderHeader: () => {
          const currentSort = sortModel.find((s) => s.field === 'updated_at');
          const isSorted = !!currentSort;
          const sortDirection = currentSort?.sort || 'desc';
          const opacity = isSorted ? 1 : 0.5;
          
          return (
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', paddingRight: 0 }}>
              <Typography variant="body2" sx={{ color: 'rgba(0, 0, 0, 0.87)', marginRight: 'auto', fontWeight: 600 }}>
                Updated
              </Typography>
              <IconButton
                size="small"
                className="sortArrowButton"
                sx={{
                  opacity: opacity,
                  color: '#ffffff',
                  padding: '4px',
                  backgroundColor: 'transparent',
                  border: 'none',
                  marginLeft: 'auto',
                  marginRight: '-8px',
                  transition: 'opacity 0.2s ease',
                  '&:hover': { opacity: 1, backgroundColor: 'transparent' },
                }}
              >
                {sortDirection === 'asc' ? (
                  <ArrowUpwardIcon fontSize="small" />
                ) : (
                  <ArrowDownwardIcon fontSize="small" />
                )}
              </IconButton>
            </Box>
          );
        },
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
          const blockedSite = params.row as BlockedSite;
          return (
            <BlockedSitesActionsCell
              blockedSite={blockedSite}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          );
        },
      },
    ],
    [onEdit, onDelete, domainSearchQuery, onDomainSearchChange, selectedCategories, onCategoryChange, allCategoryNames, sortModel],
  );
}

