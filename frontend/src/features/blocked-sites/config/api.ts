const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  blockedSites: (page?: number, pageSize?: number, domainSearch?: string) => {
    const url = new URL(`${API_BASE_URL}/blocked-sites`);
    if (page !== undefined) {
      url.searchParams.append('page', page.toString());
    }
    if (pageSize !== undefined) {
      url.searchParams.append('page_size', pageSize.toString());
    }
    if (domainSearch !== undefined && domainSearch.trim() !== '') {
      url.searchParams.append('domain_search', domainSearch.trim());
    }
    return url.toString();
  },
  blockedSite: (id: number) => `${API_BASE_URL}/blocked-sites/${id}`,
  blockedSitesCountsByCategory: () => `${API_BASE_URL}/blocked-sites/counts-by-category`,
};

export default API_BASE_URL;

