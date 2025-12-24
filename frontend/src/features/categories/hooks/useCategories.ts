import * as React from 'react';
import { Category } from '../types/category';
import { API_ENDPOINTS } from '../config/api';

export function useCategories() {
  const [categories, setCategories] = React.useState<Category[]>([]);
  const [loading, setLoading] = React.useState(true);

  const fetchCategories = React.useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.categories);
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) {
          setCategories(data);
        } else {
          console.error('Expected array but got:', typeof data, data);
          setCategories([]);
        }
      } else {
        console.error('Failed to fetch categories:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  return {
    categories,
    loading,
    fetchCategories,
    setCategories,
  };
}

