export interface Category {
  id: number;
  name: string;
  created_at?: string;
  created_by?: number | null;
  updated_at?: string;
  updated_by?: number | null;
  is_deleted: boolean;
}

export interface CategoryCreate {
  name: string;
  created_by?: number | null;
  updated_by?: number | null;
}

