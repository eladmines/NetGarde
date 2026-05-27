from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    DB_URL: str
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,https://d2qp7beltc09b8.cloudfront.net"

    # WireGuard enroll defaults (single shared pool)
    VPN_POOL_NAME: str = "default"
    VPN_POOL_CIDR: str = "10.0.0.0/24"
    VPN_GATEWAY_IP: str = "10.0.0.1"
    VPN_DNS_IP: str = "10.0.0.1"
    VPN_MTU: int = 1420
    VPN_ALLOWED_IPS: str = "0.0.0.0/0,::/0"

    VPN_ENDPOINT: str = ""
    VPN_SERVER_PUBLIC_KEY: str = ""
    VPN_PERSISTENT_KEEPALIVE: int = 25

    # Host WireGuard agent (runs on EC2 host, reachable from docker bridge)
    WG_AGENT_URL: str = "http://172.17.0.1:9109"
    WG_AGENT_TOKEN: str = ""

    # DNS ingest: when false, only blocked queries are stored in RDS (live feed uses WebSocket)
    PERSIST_ALL_DNS: bool = False

    # Anomaly detection
    NEW_DOMAIN_ALERTS: bool = True
    BANDWIDTH_ALERT_MIB_PER_SEC: float = 50.0

    # Device identity (issued at VPN enroll, used for /v1/usage and future device APIs)
    DEVICE_TOKEN_SECRET: str = ""
    DEVICE_TOKEN_TTL_DAYS: int = 365
    # Optional: require Bearer token on POST /v1/enroll (NetGardeClient --api-token)
    ENROLL_BOOTSTRAP_TOKEN: str = ""

    # Service identity: dns_log_watcher / automation posting DNS queries
    DNS_INGEST_TOKEN: str = ""

    # Admin identity: dashboard and policy APIs
    ADMIN_API_TOKEN: str = ""

    # Client behavior profiles
    # Fast-start mode: allow baseline/profile readiness with minimal data (dev/demo).
    BEHAVIOR_FAST_START: bool = False
    BEHAVIOR_BASELINE_LOOKBACK_DAYS: int = 7
    # Minimum number of hourly rollup buckets required to mark profile_ready.
    # If set > 0, this overrides BEHAVIOR_MIN_PROFILE_DAYS.
    BEHAVIOR_MIN_PROFILE_HOURS: int = 0
    BEHAVIOR_MIN_PROFILE_DAYS: int = 3
    BEHAVIOR_MIN_PROFILE_QUERIES: int = 500
    BEHAVIOR_BASELINE_RECOMPUTE_HOURS: int = 1
    BEHAVIOR_SCORE_WINDOW_MINUTES: int = 15
    BEHAVIOR_ALERT_THRESHOLD: int = 70
    BEHAVIOR_AUTO_BLOCK_THRESHOLD: int = 85
    BEHAVIOR_AUTO_BLOCK_DEFAULT: bool = False
    BEHAVIOR_AUTO_BLOCK_TTL_HOURS: int = 24
    BEHAVIOR_MAX_BLOCKS_PER_DAY: int = 10

    @property
    def device_token_secret(self) -> str:
        return self.DEVICE_TOKEN_SECRET.strip()

    @property
    def DEVICE_TOKEN_TTL_SECONDS(self) -> int:
        days = max(1, int(self.DEVICE_TOKEN_TTL_DAYS))
        return days * 24 * 60 * 60
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

