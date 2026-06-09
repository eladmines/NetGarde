/**
 * Single source for the FastAPI origin at build time (REACT_APP_API_BASE_URL).
 * Do not point this at the S3/CloudFront UI URL — that host only serves static files.
 */
export function resolveApiBaseUrl(): string {
  const raw = (process.env.REACT_APP_API_BASE_URL || '').trim();
  if (!raw) {
    return 'http://localhost:8000';
  }
  try {
    const url = new URL(raw);
    const host = url.host.toLowerCase();
    // Common misconfig: frontend CloudFront URL used as API base (returns 401/404 on /dns-queries).
    if (host.endsWith('.cloudfront.net') && !raw.includes(':8000')) {
      console.warn(
        `[TrustEdge] REACT_APP_API_BASE_URL looks like a CloudFront UI host (${host}). ` +
          'Use the API origin, e.g. http://<ec2-ip>:8000'
      );
    }
    if (host === 'google.com' || host === 'www.google.com') {
      return 'http://localhost:8000';
    }
    return raw.replace(/\/+$/, '');
  } catch {
    return 'http://localhost:8000';
  }
}

export const API_BASE_URL = resolveApiBaseUrl();
