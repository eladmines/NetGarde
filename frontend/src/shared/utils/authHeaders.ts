export function getAdminAuthHeaders(): HeadersInit {
  const token = (process.env.REACT_APP_ADMIN_API_TOKEN || '').trim();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

