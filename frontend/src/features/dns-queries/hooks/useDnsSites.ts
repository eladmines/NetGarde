import { useState, useCallback, useEffect } from 'react';
import { DnsSiteGroup, DnsSitesResponse } from '../types/dnsQuery';
import { DNS_QUERY_ENDPOINTS } from '../config/api';
import { getAdminAuthHeaders } from '../../../shared/utils/authHeaders';

export function useDnsSites() {
  const [sites, setSites] = useState<DnsSiteGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalSites, setTotalSites] = useState(0);
  const [noiseFiltered, setNoiseFiltered] = useState(0);
  const [blockedOnly, setBlockedOnly] = useState(false);
  const [filterNoise, setFilterNoise] = useState(true);

  const fetchSites = useCallback(async () => {
    try {
      setLoading(true);
      const url = DNS_QUERY_ENDPOINTS.dnsSites({
        blocked_only: blockedOnly || undefined,
        filter_noise: filterNoise,
        limit: 100,
      });

      const response = await fetch(url, { headers: getAdminAuthHeaders() });
      if (response.ok) {
        const data: DnsSitesResponse = await response.json();
        setSites(data.sites);
        setTotalSites(data.total_sites);
        setNoiseFiltered(data.noise_filtered);
      } else {
        console.error('Failed to fetch DNS sites:', response.status);
        setSites([]);
      }
    } catch (error) {
      console.error('Error fetching DNS sites:', error);
      setSites([]);
    } finally {
      setLoading(false);
    }
  }, [blockedOnly, filterNoise]);

  useEffect(() => {
    fetchSites();
  }, [fetchSites]);

  return {
    sites,
    loading,
    totalSites,
    noiseFiltered,
    blockedOnly,
    setBlockedOnly,
    filterNoise,
    setFilterNoise,
    refetch: fetchSites,
  };
}
