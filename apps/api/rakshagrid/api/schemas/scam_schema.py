# backend/fastapi/app/schemas/scam_schema.py
"""Pydantic schemas for Scam Analysis endpoints."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TextRequest(BaseModel):
    transcript: str = Field(..., description="Call or message transcript to analyze")

class StreamRequest(BaseModel):
    transcript_chunks: List[str] = Field(..., description="List of incremental transcript chunks")

class VerdictResponse(BaseModel):
    stage: str
    risk_score: float
    risk_band: str
    fired_features: List[str]
    fired_features_detail: List[Dict[str, Any]]
    component_scores: Dict[str, float]
    breakdown: Dict[str, Any]
    transcript: str
