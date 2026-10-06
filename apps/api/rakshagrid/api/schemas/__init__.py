# backend/fastapi/app/schemas/__init__.py
from .scam_schema import TextRequest, StreamRequest, VerdictResponse
from .currency_schema import CurrencyResponse
from .crime_schema import CrimeHealthResponse, HotspotsResponse, PointsResponse, PatrolAllocationResponse

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
