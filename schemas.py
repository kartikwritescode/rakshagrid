# schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TextRequest(BaseModel):
    transcript: str

class StreamRequest(BaseModel):
    transcript_chunks: List[str]

class VerdictResponse(BaseModel):
    stage: str
    risk_score: float
    risk_band: str
    fired_features: List[str]
    fired_features_detail: List[Dict[str, Any]] = []
    component_scores: Dict[str, float] = {}
    breakdown: Dict[str, Any] = {}
    transcript: Optional[str] = None