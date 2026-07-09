# schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TextRequest(BaseModel):
    transcript: str

class VerdictResponse(BaseModel):
    stage: str
    risk_score: float
    risk_band: str
    fired_features: List[str]
    breakdown: Dict[str, Any] = {}