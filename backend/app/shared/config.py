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
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

