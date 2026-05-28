export function getAdminApiToken(): string {
  return (process.env.REACT_APP_ADMIN_API_TOKEN || '').trim();
}

export function getAdminAuthHeaders(): HeadersInit {
  const token = getAdminApiToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

