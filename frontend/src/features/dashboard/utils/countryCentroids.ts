/** Approximate country centroids (WGS84) for map marker placement. */
const CENTROIDS: Record<string, { lat: number; lon: number }> = {
  AD: { lat: 42.5, lon: 1.5 },
  AE: { lat: 24.0, lon: 54.0 },
  AR: { lat: -34.0, lon: -64.0 },
  AT: { lat: 47.5, lon: 14.5 },
  AU: { lat: -25.0, lon: 134.0 },
  BE: { lat: 50.5, lon: 4.5 },
  BR: { lat: -10.0, lon: -55.0 },
  CA: { lat: 56.0, lon: -96.0 },
  CH: { lat: 47.0, lon: 8.0 },
  CN: { lat: 35.0, lon: 103.0 },
  CO: { lat: 4.0, lon: -72.0 },
  CZ: { lat: 49.8, lon: 15.5 },
  DE: { lat: 51.0, lon: 10.0 },
  DK: { lat: 56.0, lon: 10.0 },
  ES: { lat: 40.0, lon: -4.0 },
  FI: { lat: 64.0, lon: 26.0 },
  FR: { lat: 46.0, lon: 2.0 },
  GB: { lat: 54.0, lon: -2.0 },
  GR: { lat: 39.0, lon: 22.0 },
  HK: { lat: 22.3, lon: 114.2 },
  HU: { lat: 47.0, lon: 19.5 },
  IE: { lat: 53.0, lon: -8.0 },
  IL: { lat: 31.5, lon: 34.8 },
  IN: { lat: 22.0, lon: 79.0 },
  IR: { lat: 32.0, lon: 53.0 },
  IT: { lat: 42.8, lon: 12.5 },
  JP: { lat: 36.0, lon: 138.0 },
  KR: { lat: 36.5, lon: 128.0 },
  MX: { lat: 23.0, lon: -102.0 },
  NG: { lat: 9.0, lon: 8.0 },
  NL: { lat: 52.3, lon: 5.5 },
  NO: { lat: 61.0, lon: 8.0 },
  NZ: { lat: -41.0, lon: 174.0 },
  PL: { lat: 52.0, lon: 19.0 },
  PT: { lat: 39.5, lon: -8.0 },
  RO: { lat: 46.0, lon: 25.0 },
  RU: { lat: 61.0, lon: 105.0 },
  SA: { lat: 24.0, lon: 45.0 },
  SE: { lat: 62.0, lon: 15.0 },
  SG: { lat: 1.3, lon: 103.8 },
  SY: { lat: 35.0, lon: 38.0 },
  TR: { lat: 39.0, lon: 35.0 },
  TW: { lat: 23.7, lon: 121.0 },
  UA: { lat: 49.0, lon: 32.0 },
  US: { lat: 39.0, lon: -98.0 },
  ZA: { lat: -29.0, lon: 24.0 },
};

const MAP_WIDTH = 1010;
const MAP_HEIGHT = 666;

export function lonLatToMapPoint(lon: number, lat: number): { x: number; y: number } {
  return {
    x: ((lon + 180) / 360) * MAP_WIDTH,
    y: ((90 - lat) / 180) * MAP_HEIGHT,
  };
}

export function countryCodeToMapPoint(code: string | null | undefined): { x: number; y: number } | null {
  const key = (code || '').trim().toUpperCase();
  if (!key || key === 'UNKNOWN' || key === 'GLOBAL') {
    return null;
  }
  const c = CENTROIDS[key];
  if (!c) {
    return null;
  }
  return lonLatToMapPoint(c.lon, c.lat);
}

export const WORLD_MAP_VIEW_BOX = `0 0 ${MAP_WIDTH} ${MAP_HEIGHT}`;
