import type { NetworkThroughputPoint } from '../types/networkThroughput';

/** Rolling window shown on the live network chart. */
export const THROUGHPUT_HISTORY_WINDOW_MS = 60 * 60 * 1000;

export const THROUGHPUT_HISTORY_STORAGE_KEY = 'netgarde:throughput-history';

/** ~1 sample / 5s for 60 min; bucket downsampling only above this. */
export const THROUGHPUT_CHART_MAX_POINTS = 720;

export function pruneThroughputHistory(
  points: NetworkThroughputPoint[],
  now = Date.now(),
): NetworkThroughputPoint[] {
  const cutoff = now - THROUGHPUT_HISTORY_WINDOW_MS;
  return points.filter((p) => p.ts >= cutoff);
}

/** Highest single-series rate in the window (chart plots ↓ and ↑ separately, not total). */
export function peakSeriesRate(points: NetworkThroughputPoint[]): number {
  return points.reduce(
    (max, p) => Math.max(max, p.rx_mib_per_sec, p.tx_mib_per_sec),
    0,
  );
}

function peakOfPoint(p: NetworkThroughputPoint): number {
  return Math.max(p.rx_mib_per_sec, p.tx_mib_per_sec);
}

/** Fixed time buckets so adding samples does not skip past spikes (e.g. 22:20). */
export function downsampleThroughputForChart(
  points: NetworkThroughputPoint[],
  maxPoints = THROUGHPUT_CHART_MAX_POINTS,
  windowEndMs = Date.now(),
): NetworkThroughputPoint[] {
  if (points.length <= maxPoints) {
    return [...points].sort((a, b) => a.ts - b.ts);
  }

  const sorted = [...points].sort((a, b) => a.ts - b.ts);
  const bucketMs = Math.ceil(THROUGHPUT_HISTORY_WINDOW_MS / maxPoints);
  const windowStart = windowEndMs - THROUGHPUT_HISTORY_WINDOW_MS;
  const buckets = new Map<number, NetworkThroughputPoint>();

  for (const p of sorted) {
    if (p.ts < windowStart || p.ts > windowEndMs) {
      continue;
    }
    // Epoch-aligned slots so bucket assignment does not drift as the window scrolls.
    const slot = Math.floor(p.ts / bucketMs);
    const existing = buckets.get(slot);
    if (!existing || peakOfPoint(p) > peakOfPoint(existing)) {
      buckets.set(slot, p);
    }
  }

  return [...buckets.values()].sort((a, b) => a.ts - b.ts);
}

export function loadStoredThroughputHistory(): NetworkThroughputPoint[] {
  try {
    const raw = sessionStorage.getItem(THROUGHPUT_HISTORY_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as NetworkThroughputPoint[];
    if (!Array.isArray(parsed)) {
      return [];
    }
    return pruneThroughputHistory(parsed);
  } catch {
    return [];
  }
}

export function saveStoredThroughputHistory(points: NetworkThroughputPoint[]): void {
  try {
    sessionStorage.setItem(THROUGHPUT_HISTORY_STORAGE_KEY, JSON.stringify(points));
  } catch {
    /* quota or private mode */
  }
}
