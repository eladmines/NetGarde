import type { NetworkThroughputPoint } from '../types/networkThroughput';

/** Rolling window shown on the live network chart. */
export const THROUGHPUT_HISTORY_WINDOW_MS = 60 * 60 * 1000;

export const THROUGHPUT_HISTORY_STORAGE_KEY = 'netgarde:throughput-history';

/** Cap rendered points so the chart stays responsive over a full hour. */
export const THROUGHPUT_CHART_MAX_POINTS = 400;

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

export function downsampleThroughputForChart(
  points: NetworkThroughputPoint[],
  maxPoints = THROUGHPUT_CHART_MAX_POINTS,
): NetworkThroughputPoint[] {
  if (points.length <= maxPoints) {
    return points;
  }
  const step = Math.ceil(points.length / maxPoints);
  const sampled: NetworkThroughputPoint[] = [];
  for (let i = 0; i < points.length; i += step) {
    sampled.push(points[i]);
  }
  const last = points[points.length - 1];
  if (sampled[sampled.length - 1]?.ts !== last.ts) {
    sampled.push(last);
  }
  return sampled;
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
