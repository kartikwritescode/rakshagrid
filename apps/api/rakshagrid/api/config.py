# apps/api/rakshagrid/api/config.py
"""FastAPI Backend Settings and Configuration."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from rakshagrid.common.configs.base_config import artifact_config, BASE_DIR, STORAGE_DIR, UPLOADS_DIR, OUTPUTS_DIR

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

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
    
    UPLOADS_PATH: str = str(artifact_config.UPLOAD_ROOT)
    OUTPUTS_PATH: str = str(artifact_config.OUTPUT_ROOT)
    STORAGE_PATH: str = str(artifact_config.STORAGE_DIR)
    MODELS_PATH: str = str(artifact_config.MODEL_ROOT)
    DATA_PATH: str = str(artifact_config.DATA_ROOT)
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

settings = Settings()
