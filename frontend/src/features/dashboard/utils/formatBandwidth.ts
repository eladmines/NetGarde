export function formatMibPerSec(rate: number): string {
  if (!Number.isFinite(rate) || rate <= 0) {
    return '0';
  }
  if (rate < 0.01) {
    return rate.toFixed(3);
  }
  if (rate < 10) {
    return rate.toFixed(2);
  }
  return rate.toFixed(1);
}

export function formatBytesCompact(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return '0 B';
  }
  const mib = bytes / (1024 * 1024);
  if (mib >= 1) {
    return `${mib.toFixed(mib >= 10 ? 0 : 1)} MiB`;
  }
  const kib = bytes / 1024;
  if (kib >= 1) {
    return `${kib.toFixed(0)} KiB`;
  }
  return `${bytes} B`;
}
