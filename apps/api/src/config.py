# apps/api/src/config.py
"""Centralized, environment-driven configuration for Raksha Grid API."""

import os
from pathlib import Path
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from rakshagrid.common.configs.base_config import artifact_config, BASE_DIR, STORAGE_DIR, UPLOADS_DIR, OUTPUTS_DIR

class Settings(BaseSettings):
    """Production application settings loaded safely from environment variables and .env."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application metadata
    PROJECT_NAME: str = "Raksha Grid Central Intelligence API"
    VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"
    API_LEGACY_PREFIX: str = "/api"
    
    # Server runtime
    HOST: str = Field(default="0.0.0.0", description="Bind host")
    PORT: int = Field(default=8000, description="Bind port")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Application log level")
    
    # Security & CORS
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            o.strip()
            for o in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000",
            ).split(",")
            if o.strip() and o.strip() != "*"
        ],
        description="Explicit allowed CORS origins. Wildcard '*' is strictly disallowed.",
    )
    API_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("API_KEY", "rakshagrid-master-key-2026")),
        description="Master API key for sensitive intelligence and administrative endpoints",
    )
    AUTH_ENABLED: bool = Field(
        default=True,
        description="Enforce authentication on sensitive public-safety intelligence endpoints",
    )
    
    # File Upload Security
    MAX_UPLOAD_SIZE_BYTES: int = Field(
        default=25 * 1024 * 1024,  # 25 MB
        description="Maximum permitted upload size across all endpoints (25 MB)",
    )
    
    # ML Concurrency Control
    INFERENCE_MAX_CONCURRENCY: int = Field(
        default=4,
        description="Maximum concurrent CPU/GPU inference tasks to prevent event loop starvation and OOM",
    )
    
    # Storage & Artifact Paths (resolved relative to artifact_config)
    UPLOADS_PATH: str = str(artifact_config.UPLOAD_ROOT)
    OUTPUTS_PATH: str = str(artifact_config.OUTPUT_ROOT)
    STORAGE_PATH: str = str(artifact_config.STORAGE_DIR)
    MODELS_PATH: str = str(artifact_config.MODEL_ROOT)
    DATA_PATH: str = str(artifact_config.DATA_ROOT)
    CRIME_DATASET_PATH: str = Field(
        default_factory=lambda: os.getenv(
            "CRIME_DATASET_PATH",
            str(artifact_config.DATA_ROOT / "processed" / "points.parquet")
        ),
        description="Canonical dataset path for VigilGrid crime point cloud"
    )
    
    # External API Keys (kept out of source code, loaded from env)
    GROQ_API_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("GROQ_API_KEY", "")),
        description="Groq API key for LLM fallback analysis"
    )
    GROQ_MODEL_NAME: str = Field(
        default_factory=lambda: os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
    )

    @property
    def groq_key_value(self) -> str:
        """Safely extract plain secret value without leaking in string representations."""
        return self.GROQ_API_KEY.get_secret_value() if self.GROQ_API_KEY else ""

settings = Settings()
