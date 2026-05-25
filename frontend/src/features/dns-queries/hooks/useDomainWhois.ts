import { useCallback, useState } from 'react';
import { DNS_QUERY_ENDPOINTS } from '../config/api';
import { WhoisLookupResponse } from '../types/dnsQuery';

export function useDomainWhois() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<WhoisLookupResponse | null>(null);

  const lookup = useCallback(async (domain: string) => {
    const trimmed = domain.trim();
    if (!trimmed) {
      setError('No domain to look up');
      setResult(null);
      return null;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(DNS_QUERY_ENDPOINTS.dnsWhois(trimmed));
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = typeof body.detail === 'string' ? body.detail : `HTTP ${response.status}`;
        throw new Error(detail);
      }
      const data = body as WhoisLookupResponse;
      setResult(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'WHOIS lookup failed';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setResult(null);
  }, []);

  return { lookup, loading, error, result, reset };
}
