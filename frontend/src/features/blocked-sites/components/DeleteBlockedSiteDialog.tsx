import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Typography from '@mui/material/Typography';
import { BlockedSite } from '../types/blockedSite';

interface DeleteBlockedSiteDialogProps {
  open: boolean;
  blockedSite: BlockedSite | null;
  onClose: () => void;
  onConfirm: () => void;
  deleting: boolean;
}

export default function DeleteBlockedSiteDialog({
  open,
  blockedSite,
  onClose,
  onConfirm,
  deleting,
}: DeleteBlockedSiteDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Delete Blocked Site</DialogTitle>
      <DialogContent>
        <Typography>
          Are you sure you want to delete the blocked site for{' '}
          <strong>{blockedSite?.domain}</strong>?
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          This action cannot be undone.
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={deleting}>
          Cancel
        </Button>
        <Button
          onClick={onConfirm}
          variant="contained"
          color="error"
          disabled={deleting}
          sx={{
            backgroundColor: '#d32f2f',
            '&:hover': {
              backgroundColor: '#c62828',
            },
          }}
        >
          {deleting ? 'Deleting...' : 'Delete'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

