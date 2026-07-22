# backend/fastapi/app/schemas/__init__.py
from backend.fastapi.app.schemas.scam_schema import TextRequest, StreamRequest, VerdictResponse
from backend.fastapi.app.schemas.currency_schema import CurrencyResponse
from backend.fastapi.app.schemas.crime_schema import CrimeHealthResponse, HotspotsResponse, PointsResponse, PatrolAllocationResponse

__all__ = [
    "TextRequest",
    "StreamRequest",
    "VerdictResponse",
    "CurrencyResponse",
    "CrimeHealthResponse",
    "HotspotsResponse",
    "PointsResponse",
    "PatrolAllocationResponse",
]
