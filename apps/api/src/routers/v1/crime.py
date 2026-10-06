# apps/api/src/routers/v1/crime.py
"""Router for Module 4: VigilGrid Geospatial Crime Pattern Intelligence."""

import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from apps.api.src.core.security import verify_api_key

from apps.api.src.schemas.crime_schema import (
    CrimeHealthResponse,
    HotspotsResponse,
    PointsResponse,
    PatrolAllocationResponse,
    CrimeMediaNotImplementedResponse,
)
from apps.api.src.services.crime_service import crime_service

router = APIRouter(prefix="/crime", tags=["Geospatial Crime Intelligence"])


@router.get("/health", response_model=CrimeHealthResponse)
async def crime_health():
    """Returns runtime health status of the VigilGrid hotspot engine (public health probe)."""
    return await asyncio.to_thread(crime_service.get_status)


@router.get("/hotspots", response_model=HotspotsResponse, dependencies=[Depends(verify_api_key)])
async def get_hotspots():
    """Returns detected DBSCAN crime hotspot clusters ranked by composite risk weight (Protected)."""
    hotspots = await asyncio.to_thread(crime_service.get_hotspots)
    return {"hotspots": hotspots}


@router.get("/points", response_model=PointsResponse, dependencies=[Depends(verify_api_key)])
@router.get("/incidents", response_model=PointsResponse, dependencies=[Depends(verify_api_key)])
async def get_points(
    limit: int = Query(5000, description="Max points to return", ge=1, le=50000)
):
    """Returns raw incident point cloud formatted for Leaflet.js map markers (Protected)."""
    pts = await asyncio.to_thread(crime_service.get_points, limit=limit)
    return {"points": pts, "total": len(pts)}


@router.get("/patrol-allocation", response_model=PatrolAllocationResponse, dependencies=[Depends(verify_api_key)])
async def get_patrol_allocation(
    units: Optional[int] = Query(None, description="Total patrol units available", ge=0, le=500),
    n_units: Optional[int] = Query(None, description="Patrol units alias (n_units)", ge=0, le=500),
):
    """Allocates patrol resource units across hotspot clusters proportionally to risk weights (Protected)."""
    target_units = n_units if n_units is not None else (units if units is not None else 10)
    allocations = await asyncio.to_thread(crime_service.allocate_patrols, n_units=target_units)
    return {
        "n_units": target_units,
        "allocation": allocations,
    }


@router.post(
    "/predict",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=CrimeMediaNotImplementedResponse,
    dependencies=[Depends(verify_api_key)],
    responses={
        501: {
            "model": CrimeMediaNotImplementedResponse,
            "description": "Crime media analysis model is not implemented",
        }
    },
)
async def predict_crime_incident(
    city: Optional[str] = Form(None),
    crime_description: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """Crime scene media analysis and automated incident prediction is not yet implemented.

    Returns HTTP 501 Not Implemented with a structured response indicating
    that media analysis is currently unavailable. Never fabricates predictions.
    """
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "error": True,
            "code": "MEDIA_ANALYSIS_NOT_IMPLEMENTED",
            "message": "Crime media analysis is not currently available.",
        },
    )
