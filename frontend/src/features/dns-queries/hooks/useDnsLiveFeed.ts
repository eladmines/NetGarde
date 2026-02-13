import { useState, useEffect, useRef, useCallback } from 'react';

export interface LiveDnsQuery {
  timestamp: string;
  client_ip: string;
  domain: string;
  query_type: string | null;
  action: string | null;
  blocked: boolean;
}

interface WebSocketMessage {
  type: string;
  queries: LiveDnsQuery[];
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function getWebSocketUrl(): string {
  const url = new URL(API_BASE_URL);
  const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${url.host}/dns-queries/ws`;
}

const MAX_FEED_SIZE = 200; // Keep last 200 entries in memory
const RECONNECT_DELAY = 3000; // 3 seconds

export function useDnsLiveFeed() {
  const [feed, setFeed] = useState<LiveDnsQuery[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'reconnecting'>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isPausedRef = useRef(isPaused);

  // Keep ref in sync with state
  isPausedRef.current = isPaused;

  const connect = useCallback(() => {
    // Don't reconnect if already connected
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = getWebSocketUrl();
    setConnectionStatus('connecting');

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setConnectionStatus('connected');
        console.log('[LiveFeed] WebSocket connected to', wsUrl);
      };

      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          if (data.type === 'dns_queries' && data.queries?.length > 0) {
            // Only update feed if not paused
            if (!isPausedRef.current) {
              setFeed((prev) => {
                const updated = [...data.queries, ...prev];
                // Trim to max size
                return updated.slice(0, MAX_FEED_SIZE);
              });
            }
          }
        } catch (e) {
          console.warn('[LiveFeed] Failed to parse WebSocket message:', e);
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        setConnectionStatus('disconnected');
        wsRef.current = null;
        console.log('[LiveFeed] WebSocket disconnected:', event.code, event.reason);

        // Auto-reconnect unless intentionally closed
        if (event.code !== 1000) {
          setConnectionStatus('reconnecting');
          reconnectTimerRef.current = setTimeout(() => {
            console.log('[LiveFeed] Reconnecting...');
            connect();
          }, RECONNECT_DELAY);
        }
      };

      ws.onerror = (error) => {
        console.error('[LiveFeed] WebSocket error:', error);
      };
    } catch (e) {
      console.error('[LiveFeed] Failed to create WebSocket:', e);
      setConnectionStatus('disconnected');
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }
    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, []);

  const clearFeed = useCallback(() => {
    setFeed([]);
  }, []);

  const togglePause = useCallback(() => {
    setIsPaused((prev) => !prev);
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    feed,
    isConnected,
    isPaused,
    connectionStatus,
    togglePause,
    clearFeed,
    connect,
    disconnect,
  };
}
