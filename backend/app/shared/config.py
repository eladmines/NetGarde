from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

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
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

