export interface BlockedSite {
  id: number;
  domain: string;
  reason: string;
  category?: string | null;
  created_at?: string;
  updated_at?: string;
  deleted_at?: string | null;
}

export interface BlockedSiteCreate {
  domain: string;
  reason: string;
  category?: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

