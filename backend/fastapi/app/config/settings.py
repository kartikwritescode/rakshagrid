# backend/fastapi/app/config/settings.py
"""FastAPI Backend Settings and Configuration."""

import os
from pydantic_settings import BaseSettings
from shared.configs.base_config import BASE_DIR, STORAGE_DIR, UPLOADS_DIR, OUTPUTS_DIR

class Settings(BaseSettings):
    PROJECT_NAME: str = "Raksha Grid Central Intelligence API"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*"
    ]
    
    UPLOADS_PATH: str = UPLOADS_DIR
    OUTPUTS_PATH: str = OUTPUTS_DIR
    STORAGE_PATH: str = STORAGE_DIR
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
