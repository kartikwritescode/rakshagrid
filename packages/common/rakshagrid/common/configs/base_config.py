# packages/common/rakshagrid/common/configs/base_config.py
"""Centralized environment and artifact configuration management using Pydantic Settings."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict
from rakshagrid.common.exceptions.base import MissingModelArtifactError

# Load env vars from .env
load_dotenv()


def find_repo_root() -> Path:
    """Traverse up to find repository root containing .git or both apps/ and packages/."""
    cur = Path(__file__).resolve()
    for parent in [cur] + list(cur.parents):
        if (parent / ".git").exists() or ((parent / "packages").is_dir() and (parent / "apps").is_dir()):
            return parent
    return Path(__file__).resolve().parents[4]


class ArtifactConfig(BaseSettings):
    """
    Validated Pydantic configuration for all repository artifacts, datasets, and storage roots.
    Supports environment variable overrides via MODEL_ROOT, DATA_ROOT, UPLOAD_ROOT, OUTPUT_ROOT.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    BASE_DIR: Path = Field(default_factory=find_repo_root)
    
    MODEL_ROOT: Optional[Path] = Field(
        default=None,
        validation_alias=AliasChoices("MODEL_ROOT", "RAKSHAGRID_MODEL_ROOT")
    )
    DATA_ROOT: Optional[Path] = Field(
        default=None,
        validation_alias=AliasChoices("DATA_ROOT", "RAKSHAGRID_DATA_ROOT")
    )
    UPLOAD_ROOT: Optional[Path] = Field(
        default=None,
        validation_alias=AliasChoices("UPLOAD_ROOT", "RAKSHAGRID_UPLOAD_ROOT")
    )
    OUTPUT_ROOT: Optional[Path] = Field(
        default=None,
        validation_alias=AliasChoices("OUTPUT_ROOT", "RAKSHAGRID_OUTPUT_ROOT")
    )

    def model_post_init(self, __context):
        # Resolve MODEL_ROOT
        if self.MODEL_ROOT is None:
            storage_models = self.BASE_DIR / "storage" / "models"
            artifacts_models = self.BASE_DIR / "artifacts"
            if storage_models.exists():
                self.MODEL_ROOT = storage_models
            elif artifacts_models.exists():
                self.MODEL_ROOT = artifacts_models
            else:
                self.MODEL_ROOT = storage_models
        else:
            self.MODEL_ROOT = Path(self.MODEL_ROOT).resolve()

        # Resolve DATA_ROOT
        if self.DATA_ROOT is None:
            self.DATA_ROOT = self.BASE_DIR / "data"
        else:
            self.DATA_ROOT = Path(self.DATA_ROOT).resolve()

        # Resolve UPLOAD_ROOT
        if self.UPLOAD_ROOT is None:
            self.UPLOAD_ROOT = self.BASE_DIR / "storage" / "uploads"
        else:
            self.UPLOAD_ROOT = Path(self.UPLOAD_ROOT).resolve()

        # Resolve OUTPUT_ROOT
        if self.OUTPUT_ROOT is None:
            self.OUTPUT_ROOT = self.BASE_DIR / "storage" / "outputs"
        else:
            self.OUTPUT_ROOT = Path(self.OUTPUT_ROOT).resolve()

        # Ensure runtime storage directories exist
        self.UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        self.MODEL_ROOT.mkdir(parents=True, exist_ok=True)

    @property
    def STORAGE_DIR(self) -> Path:
        return self.BASE_DIR / "storage"

    def resolve_model_path(self, relative_or_name: str | Path, required: bool = True, module_name: str = "core") -> Path:
        """
        Resolves a model path from MODEL_ROOT, with fallback to BASE_DIR / artifacts.
        Raises MissingModelArtifactError if required and not found.
        """
        target = Path(relative_or_name)
        if target.is_absolute() and target.exists():
            return target

        candidate = self.MODEL_ROOT / target
        if candidate.exists():
            return candidate

        # Fallback check in BASE_DIR / artifacts
        fallback = self.BASE_DIR / "artifacts" / target
        if fallback.exists():
            return fallback

        if required:
            raise MissingModelArtifactError(
                f"Model file '{target.name}' not found at {candidate} or {fallback}.",
                module_name=module_name
            )
        return candidate

    def resolve_data_path(self, relative_or_name: str | Path, required: bool = True) -> Path:
        """
        Resolves a data file path from DATA_ROOT or OUTPUT_ROOT.
        Raises FileNotFoundError if required and not found.
        """
        target = Path(relative_or_name)
        if target.is_absolute() and target.exists():
            return target

        candidates = [
            self.DATA_ROOT / target,
            self.DATA_ROOT / "processed" / target,
            self.OUTPUT_ROOT / target,
            self.BASE_DIR / "storage" / "outputs" / target,
            self.DATA_ROOT / "raw" / target,
        ]

        for cand in candidates:
            if cand.exists():
                return cand

        if required:
            raise FileNotFoundError(
                f"Data file '{target.name}' not found in any standard data directories: {[str(c) for c in candidates]}"
            )
        return candidates[0]


# Global singleton configuration
artifact_config = ArtifactConfig()

# Backwards compatibility path attributes (str)
BASE_DIR = str(artifact_config.BASE_DIR)
STORAGE_DIR = str(artifact_config.STORAGE_DIR)
MODELS_DIR = str(artifact_config.MODEL_ROOT)
UPLOADS_DIR = str(artifact_config.UPLOAD_ROOT)
OUTPUTS_DIR = str(artifact_config.OUTPUT_ROOT)
DATA_DIR = str(artifact_config.DATA_ROOT)
