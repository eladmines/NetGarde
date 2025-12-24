import * as React from 'react';
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import EditRoundedIcon from '@mui/icons-material/EditRounded';
import DeleteOutlineRoundedIcon from '@mui/icons-material/DeleteOutlineRounded';
import { BlockedSite } from '../../types/blockedSite';

interface BlockedSitesActionsCellProps {
  blockedSite: BlockedSite;
  onEdit: (blockedSiteId: number) => void;
  onDelete: (blockedSite: BlockedSite) => void;
}

export default function BlockedSitesActionsCell({
  blockedSite,
  onEdit,
  onDelete,
}: BlockedSitesActionsCellProps) {
  return (
    <Stack direction="row" spacing={0.5}>
      <Tooltip title="Edit blocked site">
        <IconButton
          size="small"
          aria-label={`Edit ${blockedSite.domain}`}
          onClick={() => onEdit(blockedSite.id)}
        >
          <EditRoundedIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <Tooltip title="Delete blocked site">
        <IconButton
          size="small"
          color="error"
          aria-label={`Delete ${blockedSite.domain}`}
          onClick={() => onDelete(blockedSite)}
        >
          <DeleteOutlineRoundedIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </Stack>
  );
}

