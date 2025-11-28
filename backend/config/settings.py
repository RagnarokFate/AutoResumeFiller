"""Configuration settings for AutoResumeFiller Backend API.

This module uses pydantic-settings to load configuration from environment
variables with type validation and default values.
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support.
    
    Settings can be overridden via .env file or environment variables.
    All environment variables are prefixed with APP_ (optional).
    """
    
    # API Server Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8765
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["chrome-extension://*"]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Application Metadata
    APP_NAME: str = "AutoResumeFiller Backend API"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()
