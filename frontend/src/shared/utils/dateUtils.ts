/**
 * Formats a date string to a readable format
 * @param dateString - ISO date string or date string
 * @returns Formatted date string or '-' if invalid/empty
 */
export function formatDate(dateString?: string | null): string {
  if (!dateString) return '-';
  try {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
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

