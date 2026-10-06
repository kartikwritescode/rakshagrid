# apps/api/src/schemas/crime_schema.py
"""Pydantic schemas for Crime Hotspots & VigilGrid endpoints."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class CrimeHealthResponse(BaseModel):
    status: str = Field(..., description="Engine readiness status ('ready', 'data_unavailable', 'error')")
    points_loaded: int = Field(0, description="Total incident points loaded in memory")
    hotspots_found: int = Field(0, description="Total DBSCAN hotspot clusters detected")


class HotspotsResponse(BaseModel):
    hotspots: List[Dict[str, Any]] = Field(default_factory=list, description="List of detected crime hotspot clusters")


class PointsResponse(BaseModel):
    points: List[Dict[str, Any]] = Field(default_factory=list, description="List of incident records for map visualization")
    total: int = Field(0, description="Total incident records returned")


class PatrolAllocationResponse(BaseModel):
    n_units: int = Field(..., description="Total patrol resource units allocated")
    allocation: List[Dict[str, Any]] = Field(default_factory=list, description="Cluster-wise patrol unit assignments")


class CrimeMediaNotImplementedResponse(BaseModel):
    error: bool = Field(True, description="Indicates error state")
    code: str = Field("MEDIA_ANALYSIS_NOT_IMPLEMENTED", description="Specific machine-readable error code")
    message: str = Field(
        "Crime media analysis is not currently available.",
        description="Human-readable explanation of unfulfilled media analysis"
    )
