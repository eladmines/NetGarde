from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    DB_URL: str
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,https://d2qp7beltc09b8.cloudfront.net"
    AI_CLASSIFIER_ENABLED: bool = False
    OPENAI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4.1-mini"
    AI_BASE_URL: str = "https://api.openai.com/v1/chat/completions"
    AI_TIMEOUT_SECONDS: int = 20
    DOMAIN_CLASSIFIER_POLL_INTERVAL_SECONDS: int = 5
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

