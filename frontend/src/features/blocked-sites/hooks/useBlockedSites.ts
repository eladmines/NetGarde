import * as React from 'react';
import { BlockedSite, BlockedSiteCreate, PaginatedResponse } from '../types/blockedSite';
import { API_ENDPOINTS } from '../config/api';

export function useBlockedSites() {
  const [blockedSites, setBlockedSites] = React.useState<BlockedSite[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [totalCount, setTotalCount] = React.useState(0);
  const [page, setPage] = React.useState(1);
  const [pageSize, setPageSize] = React.useState(10);
  const [domainSearch, setDomainSearch] = React.useState('');

  const fetchBlockedSites = React.useCallback(async (currentPage: number, currentPageSize: number, currentDomainSearch?: string) => {
    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.blockedSites(currentPage, currentPageSize, currentDomainSearch));
      if (response.ok) {
        const data: PaginatedResponse<BlockedSite> = await response.json();
        console.log('Fetched blocked sites data:', data);
        if (data.items && Array.isArray(data.items)) {
          setBlockedSites(data.items);
          setTotalCount(data.total);
          setPage(data.page);
          setPageSize(data.page_size);
        } else {
          console.error('Expected paginated response but got:', typeof data, data);
          setBlockedSites([]);
          setTotalCount(0);
        }
      } else {
        console.error('Failed to fetch blocked sites:', response.status, response.statusText);
        setBlockedSites([]);
        setTotalCount(0);
      }
    } catch (error) {
      console.error('Error fetching blocked sites:', error);
      setBlockedSites([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    // Reset to page 1 when domain search changes
    setPage(1);
  }, [domainSearch]);

  React.useEffect(() => {
    fetchBlockedSites(page, pageSize, domainSearch);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, domainSearch]); // fetchBlockedSites is intentionally excluded to avoid circular dependency

  return {
    blockedSites,
    loading,
    totalCount,
    page,
    pageSize,
    setPage,
    setPageSize,
    domainSearch,
    setDomainSearch,
    fetchBlockedSites,
    setBlockedSites,
  };
}

