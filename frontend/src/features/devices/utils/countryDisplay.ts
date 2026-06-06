/** ISO 3166-1 alpha-2 → flag emoji (GLOBAL/UNKNOWN → globe). */
export function countryFlagEmoji(code: string | null | undefined): string {
  const c = (code || '').toUpperCase();
  if (!c || c === 'GLOBAL' || c === 'UNKNOWN' || c.length !== 2) {
    return '🌐';
  }
  const base = 0x1f1e6;
  return String.fromCodePoint(
    ...[...c].map((ch) => base + ch.charCodeAt(0) - 65),
  );
}

export function countryLabel(
  code: string | null | undefined,
  name: string | null | undefined,
): string {
  if (!code) return '—';
  const flag = countryFlagEmoji(code);
  const label = name || code;
  return `${flag} ${label}`;
}
