import { useState, useCallback, useEffect } from 'react';
import { BlockedSite, PaginatedResponse } from '../types/blockedSite';
import { API_ENDPOINTS } from '../config/api';

export function useBlockedSites() {
  const [blockedSites, setBlockedSites] = useState<BlockedSite[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [domainSearch, setDomainSearch] = useState('');

  const fetchBlockedSites = useCallback(async (currentPage: number, currentPageSize: number, currentDomainSearch?: string) => {
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

  useEffect(() => {
    setPage(1);
  }, [domainSearch]);

  useEffect(() => {
    fetchBlockedSites(page, pageSize, domainSearch);
  }, [page, pageSize, domainSearch, fetchBlockedSites]); 

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

