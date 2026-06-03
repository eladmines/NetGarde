import { PolicyPack } from '../types/policy';

/** Exact count with thousands separators (matches server-side unique domain count). */
export function formatBlockedSiteCount(count: number): string {
  return count.toLocaleString();
}

export function packListSiteCount(pack: PolicyPack): number {
  return pack.domain_count;
}

export function packBlockingSiteCount(pack: PolicyPack): number {
  if (pack.blocked_sites_count != null) {
    return pack.blocked_sites_count;
  }
  return pack.enabled_globally ? pack.domain_count : 0;
}

export function totalBlockingSiteCount(packs: PolicyPack[]): number {
  return packs.reduce((sum, pack) => sum + packBlockingSiteCount(pack), 0);
}

export function totalListSiteCount(packs: PolicyPack[]): number {
  return packs.reduce((sum, pack) => sum + packListSiteCount(pack), 0);
}

export function packCountBySlug(packs: PolicyPack[]): Record<string, number> {
  return Object.fromEntries(packs.map((p) => [p.slug, p.domain_count]));
}
