# apps/api/src/routers/v1/audio.py
"""Router for Audio Voice Biometrics & Speech Transcription."""

import io
from fastapi import APIRouter, UploadFile, File, status
from apps.api.src.schemas.audio_schema import AudioDetectResponse, TranscribeResponse
from apps.api.src.services.audio_service import audio_service
from apps.api.src.core.upload_security import (
    ALLOWED_AUDIO_EXTENSIONS,
    read_and_validate_upload,
)
from apps.api.src.core.concurrency import inference_concurrency

router = APIRouter(prefix="/audio", tags=["Audio Deepfake & Speech-to-Text"])


@router.post("/detect", response_model=AudioDetectResponse, status_code=status.HTTP_200_OK)
async def detect_audio_deepfake(file: UploadFile = File(...)):
    """
    Analyzes an uploaded audio recording (.ogg, .mp3, .wav, etc.) for scam patterns.
    
    Hardened pipeline:
    1. Enforces 25 MB max upload limit.
    2. Validates filename and authentic binary magic bytes.
    3. Executes STT and voice biometrics via isolated concurrency-controlled thread pool.
    4. Decouples acoustic biometrics from linguistic scam analysis.
    """
    audio_bytes, safe_filename, genuine_mime = await read_and_validate_upload(
        file=file,
        allowed_extensions=ALLOWED_AUDIO_EXTENSIONS,
        allowed_mime_prefixes=("audio/",),
    )

    result = await inference_concurrency.run(
        audio_service.detect_deepfake,
        io.BytesIO(audio_bytes),
        safe_filename,
    )
    return result


@router.post("/transcribe", response_model=TranscribeResponse, status_code=status.HTTP_200_OK)
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """
    Transcribes call audio file (.ogg, .mp3, .wav, etc.) to text using Whisper.
    
    Hardened pipeline:
    1. Enforces 25 MB max upload limit and magic byte signatures.
    2. Runs asynchronously on worker thread with concurrency throttling.
    3. Returns structured failure status if STT fails without fabricating content.
    """
    audio_bytes, safe_filename, genuine_mime = await read_and_validate_upload(
        file=file,
        allowed_extensions=ALLOWED_AUDIO_EXTENSIONS,
        allowed_mime_prefixes=("audio/",),
    )

    result = await inference_concurrency.run(
        audio_service.transcribe,
        io.BytesIO(audio_bytes),
        safe_filename,
    )
    return result

