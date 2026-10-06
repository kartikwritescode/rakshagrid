# backend/fastapi/app/schemas/currency_schema.py
"""Pydantic schemas for Currency Counterfeit Analysis endpoints."""

from pydantic import BaseModel
from typing import Dict, Optional

class CurrencyResponse(BaseModel):
    status: str
    predicted_label: str
    confidence: float
    is_genuine: bool
    class_probabilities: Dict[str, float]
    calibrated_verdict: Optional[str] = None
    confidence_threshold: Optional[float] = None
    processing_time_ms: Optional[float] = None

