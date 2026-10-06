# backend/fastapi/app/routers/scam_router.py
"""Router for Module 2: Scam Call Interceptor & Digital Arrest Detection."""

import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from rakshagrid.api.schemas.scam_schema import TextRequest, StreamRequest, VerdictResponse
from rakshagrid.api.services.scam_service import scam_service

router = APIRouter(prefix="/scam", tags=["Scam Call Interceptor"])

ALLOWED_AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".ogg", ".opus", ".m4a", ".aac", ".flac", ".webm", ".wma", ".mp4"
}

@router.post("/analyze-text", response_model=VerdictResponse, status_code=status.HTTP_200_OK)
def analyze_text(payload: TextRequest):
    """Analyzes a call or message transcript through the feature-augmented stacked ensemble pipeline."""
    if not payload.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty.")
    return scam_service.analyze_text(payload.transcript)

@router.post("/analyze-audio", response_model=VerdictResponse, status_code=status.HTTP_200_OK)
async def analyze_audio(file: UploadFile = File(...)):
    """Uploads and transcribes a call audio recording (.ogg, .wav, .mp3, .m4a, etc.) using Whisper."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext and ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed audio formats: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
        )
    
    filename = file.filename or "recording.ogg"
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, f"upload_{filename}")
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return scam_service.analyze_audio(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

@router.post("/stream", status_code=status.HTTP_200_OK)
def analyze_stream(payload: StreamRequest):
    """Generates incremental risk evaluations for transcript chunks."""
    if not payload.transcript_chunks:
        raise HTTPException(status_code=400, detail="transcript_chunks cannot be empty.")
    return scam_service.analyze_stream(payload.transcript_chunks)
