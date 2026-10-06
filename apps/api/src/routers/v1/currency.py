# apps/api/src/routers/v1/currency.py
"""Router for Module 1: Counterfeit Currency Detection."""

from fastapi import APIRouter, UploadFile, File, status
from apps.api.src.schemas.currency_schema import CurrencyResponse
from apps.api.src.services.currency_service import currency_service
from apps.api.src.core.upload_security import (
    ALLOWED_IMAGE_EXTENSIONS,
    read_and_validate_upload,
)
from apps.api.src.core.concurrency import inference_concurrency

router = APIRouter(prefix="/currency", tags=["Counterfeit Currency Identification"])


@router.post("/predict", response_model=CurrencyResponse, status_code=status.HTTP_200_OK)
@router.post("/analyze-image", response_model=CurrencyResponse, status_code=status.HTTP_200_OK)
async def analyze_currency(file: UploadFile = File(...)):
    """
    Analyzes a currency banknote image for counterfeit defects and authenticity.
    
    Hardened pipeline:
    1. Enforces 25 MB max upload ceiling.
    2. Validates filename against path traversal.
    3. Verifies authentic binary magic bytes (JPEG/PNG/WebP).
    4. Executes TensorFlow inference via isolated concurrency-controlled thread pool.
    """
    image_bytes, safe_filename, genuine_mime = await read_and_validate_upload(
        file=file,
        allowed_extensions=ALLOWED_IMAGE_EXTENSIONS,
        allowed_mime_prefixes=("image/",),
    )

    result = await inference_concurrency.run(
        currency_service.analyze_image,
        image_bytes=image_bytes,
        filename=safe_filename,
        content_type=genuine_mime,
    )
    return result



