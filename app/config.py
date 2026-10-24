"""Application configuration with Pydantic Settings."""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Task Manager"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Logging
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Server Ports
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    UI_PORT: int = 8501
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/tasks.db"
    
    # Gemini AI Configuration (optional, graceful fallback if missing)
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Path to legacy tasks file
    LEGACY_TASKS_FILE: str = "tasks.json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
