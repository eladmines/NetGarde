import { useCallback, useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import RefreshIcon from '@mui/icons-material/Refresh';
import SearchIcon from '@mui/icons-material/Search';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { policyApi } from '../config/api';
import { PolicyPack } from '../types/policy';
const PAGE_SIZE = 50;

export interface PolicyPackDomainsDialogProps {
  pack: PolicyPack | null;
  open: boolean;
  onClose: () => void;
  onPackUpdated: (pack: PolicyPack) => void;
}

export default function PolicyPackDomainsDialog({
  pack,
  open,
  onClose,
  onPackUpdated,
}: PolicyPackDomainsDialogProps) {
  const [domains, setDomains] = useState<string[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [source, setSource] = useState<string>('seed');
  const [searchInput, setSearchInput] = useState('');
  const [appliedQuery, setAppliedQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPage = useCallback(async () => {
    if (!pack) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const page = await policyApi.listPackDomains(pack.slug, {
        q: appliedQuery,
        skip,
        limit: PAGE_SIZE,
      });
      setDomains(page.domains);
      setTotal(page.total);
      setSource(page.domain_list_source);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load domains');
      setDomains([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [pack, appliedQuery, skip]);

  useEffect(() => {
    if (!open || !pack) {
      return;
    }
    loadPage();
  }, [open, pack, loadPage]);

  useEffect(() => {
    if (!open) {
      setSkip(0);
      setSearchInput('');
      setAppliedQuery('');
      setError(null);
    }
  }, [open]);

  const handleSearch = () => {
    setSkip(0);
    setAppliedQuery(searchInput.trim());
  };

  const handleRefreshUpstream = async () => {
    if (!pack) {
      return;
    }
    setRefreshing(true);
    setError(null);
    try {
      const result = await policyApi.refreshPack(pack.slug);
      onPackUpdated({
        ...pack,
        domain_count: result.domain_count,
        blocked_sites_count: pack.enabled_globally ? result.domain_count : 0,
        domain_list_source: 'snapshot',
      });
      setSkip(0);
      await loadPage();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to update from upstream');
    } finally {
      setRefreshing(false);
    }
  };

  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const pageIndex = Math.floor(skip / PAGE_SIZE) + 1;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {pack ? `${pack.name} — blocked sites` : 'Blocked sites'}
      </DialogTitle>
      <DialogContent dividers>
        {pack && (
          <Stack spacing={2}>
            <Typography variant="body2" color="text.secondary">
              {source === 'snapshot' ? 'Full list on server' : 'Seed list — use Update from upstream for full list'}
              {appliedQuery ? ` · filtered by “${appliedQuery}”` : ''}
            </Typography>

            <Stack direction="row" spacing={1}>
              <TextField
                size="small"
                fullWidth
                placeholder="Search domains…"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon fontSize="small" />
                    </InputAdornment>
                  ),
                }}
              />
              <Button variant="outlined" onClick={handleSearch} disabled={loading}>
                Search
              </Button>
            </Stack>

            {error && (
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            <Box
              sx={{
                minHeight: 280,
                maxHeight: 360,
                overflow: 'auto',
                border: 1,
                borderColor: 'divider',
                borderRadius: 1,
              }}
            >
              {loading ? (
                <Stack alignItems="center" justifyContent="center" sx={{ py: 8 }}>
                  <CircularProgress size={32} />
                </Stack>
              ) : domains.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
                  No domains match.
                </Typography>
              ) : (
                <List dense disablePadding>
                  {domains.map((domain) => (
                    <ListItem key={domain} divider>
                      <ListItemText primary={domain} primaryTypographyProps={{ fontFamily: 'monospace' }} />
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>

            <Stack direction="row" alignItems="center" justifyContent="space-between">
              <Typography variant="caption" color="text.secondary">
                Page {pageIndex} of {pageCount}
              </Typography>
              <Stack direction="row" spacing={0.5}>
                <IconButton
                  size="small"
                  disabled={loading || skip === 0}
                  onClick={() => setSkip((s) => Math.max(0, s - PAGE_SIZE))}
                  aria-label="Previous page"
                >
                  <ChevronLeftIcon />
                </IconButton>
                <IconButton
                  size="small"
                  disabled={loading || skip + PAGE_SIZE >= total}
                  onClick={() => setSkip((s) => s + PAGE_SIZE)}
                  aria-label="Next page"
                >
                  <ChevronRightIcon />
                </IconButton>
              </Stack>
            </Stack>
          </Stack>
        )}
      </DialogContent>
      <DialogActions>
        <Button
          startIcon={refreshing ? <CircularProgress size={16} /> : <RefreshIcon />}
          onClick={handleRefreshUpstream}
          disabled={refreshing || !pack}
        >
          Update from upstream
        </Button>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}
