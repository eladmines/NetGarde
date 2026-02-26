import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import Chip from '@mui/material/Chip';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import { useDnsQueries } from '../../dns-queries/hooks/useDnsQueries';
import { formatDateTime } from '../../../shared/utils/dateUtils';

function renderBlockedStatus(params: GridRenderCellParams) {
  return (
    <Chip
      label={params.value ? 'Blocked' : 'Allowed'}
      color={params.value ? 'error' : 'success'}
      size="small"
      variant="outlined"
    />
  );
}

function renderAction(params: GridRenderCellParams) {
  const actionColors: Record<string, 'error' | 'success' | 'info' | 'default'> = {
    blocked: 'error',
    forwarded: 'success',
    cached: 'info',
  };
  const color = actionColors[params.value as string] || 'default';
  return <Chip label={params.value || 'unknown'} color={color} size="small" />;
}

function formatTimestamp(params: GridRenderCellParams) {
  return formatDateTime(params.value as string);
}

function renderMachine(params: GridRenderCellParams) {
  const deviceName = params.row.device_name as string | null | undefined;
  const deviceVendor = params.row.device_vendor as string | null | undefined;
  const clientIp = params.row.client_ip as string;

  return (
    <Stack spacing={0} sx={{ py: 0.5 }}>
      <Typography variant="body2" sx={{ fontWeight: 500, lineHeight: 1.2 }}>
        {deviceName || 'Unknown device'}
      </Typography>
      <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace', lineHeight: 1.2 }}>
        {deviceVendor ? `${deviceVendor} - ${clientIp}` : clientIp}
      </Typography>
    </Stack>
  );
}

const columns: GridColDef[] = [
  {
    field: 'timestamp',
    headerName: 'Time',
    flex: 1.2,
    minWidth: 160,
    renderCell: formatTimestamp,
  },
  {
    field: 'domain',
    headerName: 'Domain',
    flex: 2,
    minWidth: 200,
  },
  {
    field: 'device_name',
    headerName: 'Machine',
    flex: 1.1,
    minWidth: 170,
    sortable: false,
    renderCell: renderMachine,
  },
  {
    field: 'query_type',
    headerName: 'Type',
    flex: 0.5,
    minWidth: 70,
  },
  {
    field: 'action',
    headerName: 'Action',
    flex: 0.8,
    minWidth: 100,
    renderCell: renderAction,
  },
  {
    field: 'blocked',
    headerName: 'Status',
    flex: 0.8,
    minWidth: 100,
    renderCell: renderBlockedStatus,
  },
];

export default function CustomizedDataGrid() {
  const {
    queries,
    loading,
    totalCount,
    page,
    pageSize,
    setPage,
    setPageSize,
    domainSearch,
    setDomainSearch,
    blockedOnly,
    setBlockedOnly,
  } = useDnsQueries();

  if (loading && queries.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Stack direction="row" spacing={2} sx={{ mb: 2, alignItems: 'center' }}>
        <TextField
          size="small"
          placeholder="Search domain..."
          value={domainSearch}
          onChange={(e) => setDomainSearch(e.target.value)}
          sx={{ minWidth: 220 }}
        />
        <FormControlLabel
          control={
            <Switch
              checked={blockedOnly}
              onChange={(e) => setBlockedOnly(e.target.checked)}
              size="small"
            />
          }
          label={<Typography variant="body2">Blocked only</Typography>}
        />
        <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
          {totalCount.toLocaleString()} total queries
        </Typography>
      </Stack>
      <DataGrid
        rows={queries}
        columns={columns}
        loading={loading}
        rowCount={totalCount}
        paginationMode="server"
        paginationModel={{ page: page - 1, pageSize }}
        onPaginationModelChange={(model) => {
          setPage(model.page + 1);
          setPageSize(model.pageSize);
        }}
        pageSizeOptions={[10, 20, 50]}
        disableRowSelectionOnClick
        disableColumnResize
        density="compact"
        getRowClassName={(params) =>
          params.row.blocked ? 'blocked-row' : params.indexRelativeToCurrentPage % 2 === 0 ? 'even' : 'odd'
        }
        sx={{
          '& .blocked-row': {
            backgroundColor: 'rgba(211, 47, 47, 0.04)',
          },
        }}
        initialState={{
          pagination: { paginationModel: { pageSize: 20 } },
        }}
        slotProps={{
          filterPanel: {
            filterFormProps: {
              logicOperatorInputProps: {
                variant: 'outlined',
                size: 'small',
              },
              columnInputProps: {
                variant: 'outlined',
                size: 'small',
                sx: { mt: 'auto' },
              },
              operatorInputProps: {
                variant: 'outlined',
                size: 'small',
                sx: { mt: 'auto' },
              },
              valueInputProps: {
                InputComponentProps: {
                  variant: 'outlined',
                  size: 'small',
                },
              },
            },
          },
        }}
      />
    </Box>
  );
}
