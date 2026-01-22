const API_BASE_URL = "https://daemixzdg8jfd.cloudfront.net"

export const API_ENDPOINTS = {
  categories: `${API_BASE_URL}/categories`,
  category: (id: number) => `${API_BASE_URL}/categories/${id}`,
};

export default API_BASE_URL;

