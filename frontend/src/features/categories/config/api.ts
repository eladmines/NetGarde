const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  categories: `${API_BASE_URL}/categories`,
  category: (id: number) => `${API_BASE_URL}/categories/${id}`,
};

export default API_BASE_URL;

