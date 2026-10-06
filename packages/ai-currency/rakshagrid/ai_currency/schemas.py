# packages/ai-currency/rakshagrid/ai_currency/schemas.py
"""Pydantic schemas for Counterfeit Currency Identification results and validation."""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class CurrencyResponse(BaseModel):
    """Structured response returned by currency analysis endpoint and service."""
    status: str = Field(..., description="Overall verdict ('genuine' or 'counterfeit')")
    predicted_label: str = Field(..., description="Top predicted class name")
    confidence: float = Field(..., description="Softmax confidence of the top prediction")
    is_genuine: bool = Field(..., description="Boolean flag: True if genuine above threshold")
    class_probabilities: Dict[str, float] = Field(
        ...,
        description="Per-defect probability distribution across all 5 classes"
    )
    calibrated_verdict: str = Field(
        ...,
        description="Calibrated verdict ('authentic', 'counterfeit_defect', 'suspicious_low_confidence')"
    )
    confidence_threshold: float = Field(
        ...,
        description="Calibrated probability threshold applied to verify authenticity"
    )
    processing_time_ms: Optional[float] = Field(
        None,
        description="End-to-end inference and postprocessing latency in milliseconds"
    )


class CurrencyValidationResult(BaseModel):
    """Details from uploaded image validation."""
    is_valid: bool = Field(..., description="Whether file meets validation criteria")
    mime_type: str = Field(..., description="Detected MIME type based on magic bytes")
    file_size_bytes: int = Field(..., description="Uploaded file size in bytes")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")
