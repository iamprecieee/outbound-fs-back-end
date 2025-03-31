from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

    # FreeSWITCH settings
    FREESWITCH_HOST: str = "65.109.11.13"
    FREESWITCH_PORT: int = 8021
    FREESWITCH_PASSWORD: str = "Outbound-123"
    CALLER_ID: Optional[str] = None
    GATEWAY: Optional[str] = None

    # Logging settings
    LOG_LEVEL: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create settings instance
settings = Settings() 
