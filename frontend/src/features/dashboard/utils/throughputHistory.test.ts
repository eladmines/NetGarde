import {
  downsampleThroughputForChart,
  THROUGHPUT_CHART_MAX_POINTS,
  THROUGHPUT_HISTORY_WINDOW_MS,
} from './throughputHistory';
import type { NetworkThroughputPoint } from '../types/networkThroughput';

function point(ts: number, rx: number): NetworkThroughputPoint {
  return {
    ts,
    label: '',
    rx_mib_per_sec: rx,
    tx_mib_per_sec: 0,
    total_mib_per_sec: rx,
    reporting_clients: 1,
  };
}

describe('downsampleThroughputForChart', () => {
  it('keeps the highest spike in each time bucket when downsampling', () => {
    const windowEnd = 1_000_000;
    const windowStart = windowEnd - THROUGHPUT_HISTORY_WINDOW_MS;
    const bucketMs = Math.ceil(THROUGHPUT_HISTORY_WINDOW_MS / 10);
    const spikeTs = windowStart + bucketMs + 1000;

    const points: NetworkThroughputPoint[] = [];
    for (let i = 0; i < 50; i += 1) {
      const ts = windowStart + i * (bucketMs / 2);
      points.push(point(ts, 0.1));
    }
    points.push(point(spikeTs, 3.0));

    const sampled = downsampleThroughputForChart(points, 10, windowEnd);
    const hasSpike = sampled.some((p) => p.rx_mib_per_sec === 3.0);
    expect(hasSpike).toBe(true);
  });

  it('does not drop points below maxPoints', () => {
    const windowEnd = Date.now();
    const points = Array.from({ length: 100 }, (_, i) =>
      point(windowEnd - (100 - i) * 5000, 0.5),
    );
    expect(downsampleThroughputForChart(points, THROUGHPUT_CHART_MAX_POINTS, windowEnd).length).toBe(
      100,
    );
  });
});
