import { useCallback, useEffect, useState } from 'react';
import { policyApi } from '../config/api';
import { PolicySyncStatus } from '../types/policy';
import { formatShortDateTime } from '../../../shared/utils/dateUtils';

const SYNC_POLL_MS = 8000;

export function policySyncStatusLabel(status: PolicySyncStatus | null): string {
  if (!status?.last_sync_at) {
    return 'Not applied to dnsmasq yet';
  }
  const when = formatShortDateTime(status.last_sync_at);
  if (status.last_success === false) {
    return `Last apply failed · ${when}`;
  }
  return `Last applied · ${when}`;
}

export function usePolicyDnsSync() {
  const [syncStatus, setSyncStatus] = useState<PolicySyncStatus | null>(null);
  const [applying, setApplying] = useState(false);
  const [applyError, setApplyError] = useState<string | null>(null);
  const [applyInfo, setApplyInfo] = useState<string | null>(null);

  const loadSyncStatus = useCallback(async () => {
    try {
      const status = await policyApi.getSyncStatus();
      setSyncStatus(status);
    } catch {
      /* optional on older backends */
    }
  }, []);

  useEffect(() => {
    loadSyncStatus();
    const id = window.setInterval(loadSyncStatus, SYNC_POLL_MS);
    return () => window.clearInterval(id);
  }, [loadSyncStatus]);

  const applyNow = async () => {
    setApplying(true);
    setApplyError(null);
    try {
      const result = await policyApi.applyPolicy();
      setApplyInfo(result.message);
      await loadSyncStatus();
    } catch (e) {
      setApplyError(e instanceof Error ? e.message : 'Failed to queue policy apply');
    } finally {
      setApplying(false);
    }
  };

  return {
    syncStatus,
    syncStatusLabel: policySyncStatusLabel(syncStatus),
    applying,
    applyError,
    setApplyError,
    applyInfo,
    setApplyInfo,
    applyNow,
    loadSyncStatus,
  };
}
