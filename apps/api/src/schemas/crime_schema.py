# backend/fastapi/app/schemas/crime_schema.py
"""Pydantic schemas for Crime Hotspots & VigilGrid endpoints."""

from pydantic import BaseModel
from typing import List, Dict, Any

class CrimeHealthResponse(BaseModel):
    status: str
    points_loaded: int
    hotspots_found: int

class HotspotsResponse(BaseModel):
    hotspots: List[Dict[str, Any]]

class PointsResponse(BaseModel):
    points: List[Dict[str, Any]]

class PatrolAllocationResponse(BaseModel):
    n_units: int
    allocation: List[Dict[str, Any]]
