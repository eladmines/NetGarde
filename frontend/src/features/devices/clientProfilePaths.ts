export function clientProfilePath(deviceId: number): string {
  return `/client-profiles?device=${deviceId}`;
}

export function parseDeviceIdParam(value: string | null): number | null {
  if (!value) return null;
  const id = Number.parseInt(value, 10);
  return Number.isFinite(id) && id > 0 ? id : null;
}
