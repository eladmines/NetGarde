/**
 * Convert a backend UTC timestamp to a local Date object.
 * Backend sends timezone-aware timestamps (e.g. "2026-02-14T19:30:15+00:00").
 * The 'Z' fallback handles any edge case where a naive timestamp is received.
 */
function toLocalDate(timestamp: string): Date {
  const ts = timestamp.endsWith('Z') || timestamp.includes('+') ? timestamp : timestamp + 'Z';
  return new Date(ts);
}

/** Full date + time: "Feb 14, 07:30 PM" */
export function formatDate(dateString?: string | null): string {
  if (!dateString) return '-';
  try {
    return toLocalDate(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateString;
  }
}

/** Date + time with seconds (24h): "Feb 14, 19:30:15" */
export function formatDateTime(timestamp?: string | null): string {
  if (!timestamp) return '';
  return toLocalDate(timestamp).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

/** Time only (24h): "19:30:15" */
export function formatTime(timestamp?: string | null): string {
  if (!timestamp) return '';
  return toLocalDate(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

/** Short date + time (24h, no seconds): "Feb 14, 19:30" */
export function formatShortDateTime(timestamp?: string | null): string {
  if (!timestamp) return '';
  return toLocalDate(timestamp).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}