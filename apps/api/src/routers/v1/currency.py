# backend/fastapi/app/routers/currency_router.py
"""Router for Module 1: Counterfeit Currency Detection."""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
try:
    from apps.api.src.schemas.currency_schema import CurrencyResponse
    from apps.api.src.services.currency_service import currency_service
except ImportError:
    from schemas.currency_schema import CurrencyResponse
    from services.currency_service import currency_service

router = APIRouter(prefix="/api/currency", tags=["Counterfeit Currency Identification"])

@router.post("/predict", response_model=CurrencyResponse, status_code=status.HTTP_200_OK)
@router.post("/analyze-image", response_model=CurrencyResponse, status_code=status.HTTP_200_OK)
async def analyze_currency(file: UploadFile = File(...)):
    """Analyzes a currency banknote image for counterfeit defects and authenticity."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Must be an image."
        )
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    import time
    start_time = time.time()
    res = currency_service.analyze_image(contents)
    res["processing_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return res
