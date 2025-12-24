import * as React from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PrimaryButton from '../../../shared/components/PrimaryButton';
import { BlockedSite } from '../types/blockedSite';
import { formatDate } from '../../../shared/utils/dateUtils';

interface BlockedSiteDetailsDialogProps {
  open: boolean;
  blockedSite: BlockedSite | null;
  onClose: () => void;
  onEdit: (blockedSiteId: number) => void;
  onDelete: (blockedSite: BlockedSite) => void;
}

export default function BlockedSiteDetailsDialog({
  open,
  blockedSite,
  onClose,
  onEdit,
  onDelete,
}: BlockedSiteDetailsDialogProps) {
  if (!blockedSite) {
    return null;
  }

  const handleEdit = () => {
    onEdit(blockedSite.id);
    onClose();
  };

  const handleDelete = () => {
    onDelete(blockedSite);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Blocked Site Details</DialogTitle>
      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              Domain
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {blockedSite.domain}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              Category
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {blockedSite.category || 'No category'}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              Reason
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {blockedSite.reason}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              Created
            </Typography>
            <Typography variant="body2">
              {blockedSite.created_at ? formatDate(blockedSite.created_at) : 'N/A'}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              Last Updated
            </Typography>
            <Typography variant="body2">
              {blockedSite.updated_at ? formatDate(blockedSite.updated_at) : 'N/A'}
            </Typography>
          </Box>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={handleDelete}
          variant="outlined"
          color="error"
          startIcon={<DeleteIcon />}
          sx={{ mr: 'auto' }}
        >
          Delete
        </Button>
        <Button onClick={onClose} variant="outlined">
          Close
        </Button>
        <PrimaryButton onClick={handleEdit} startIcon={<EditIcon />}>
          Edit
        </PrimaryButton>
      </DialogActions>
    </Dialog>
  );
}

