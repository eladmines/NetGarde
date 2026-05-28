import type { LiveDnsQuery } from './hooks/useDnsLiveFeed';

/** Last DNS activity per client IP (ms since epoch), updated from the live feed. */
const lastActivityMs: Record<string, number> = {};
const listeners = new Set<() => void>();

const ACTIVE_WINDOW_MS = 5 * 60 * 1000;

export function recordDnsClientActivity(queries: LiveDnsQuery[]): void {
  const now = Date.now();
  let changed = false;
  for (const q of queries) {
    if (!q.client_ip) continue;
    const prev = lastActivityMs[q.client_ip];
    if (prev !== now) {
      lastActivityMs[q.client_ip] = now;
      changed = true;
    }
  }
  if (changed) {
    listeners.forEach((fn) => fn());
  }
}

export function isClientActiveNow(clientIp: string): boolean {
  const last = lastActivityMs[clientIp];
  if (!last) return false;
  return Date.now() - last < ACTIVE_WINDOW_MS;
}

export function getClientLastActivityMs(clientIp: string): number | undefined {
  return lastActivityMs[clientIp];
}

export function subscribeDnsClientActivity(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
