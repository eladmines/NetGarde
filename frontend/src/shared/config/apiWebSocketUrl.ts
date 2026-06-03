import { API_BASE_URL } from './apiBaseUrl';
import { getAdminApiToken } from '../utils/authHeaders';

/** WebSocket URL for live DNS feed (admin token as query param). */
export function getDnsQueriesWebSocketUrl(): string {
  const url = new URL(API_BASE_URL);
  const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = new URL(`${protocol}//${url.host}/dns-queries/ws`);
  const token = getAdminApiToken();
  if (token) {
    wsUrl.searchParams.set('token', token);
  }
  return wsUrl.toString();
}

/** WebSocket URL for live VPN usage / bandwidth dashboard. */
export function getUsageWebSocketUrl(): string {
  const url = new URL(API_BASE_URL);
  const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = new URL(`${protocol}//${url.host}/devices/usage/ws`);
  const token = getAdminApiToken();
  if (token) {
    wsUrl.searchParams.set('token', token);
  }
  return wsUrl.toString();
}
