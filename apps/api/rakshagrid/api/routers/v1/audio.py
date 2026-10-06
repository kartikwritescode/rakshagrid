# backend/fastapi/app/routers/audio_router.py
"""Router for Module 2 & 3: Audio Deepfake Detection & Speech Transcription."""

import os
import shutil
import tempfile
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from rakshagrid.api.services.scam_service import scam_service
from rakshagrid.ai_scam.model.audio import transcribe_audio

router = APIRouter(prefix="/audio", tags=["Audio Deepfake & Speech-to-Text"])

ALLOWED_AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".ogg", ".opus", ".m4a", ".aac", ".flac", ".webm", ".wma", ".mp4"
}

@router.post("/detect", status_code=status.HTTP_200_OK)
async def detect_audio_deepfake(file: UploadFile = File(...)):
    """Analyzes an uploaded audio recording (.ogg, .mp3, .wav, etc.) for deepfake/scam markers."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext and ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed audio formats: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
        )
    
    start_time = time.time()
    temp_dir = tempfile.mkdtemp()
    filename = file.filename or "recording.ogg"
    temp_path = os.path.join(temp_dir, f"upload_{filename}")
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        res = scam_service.analyze_audio(temp_path)
        res["processing_time_ms"] = round((time.time() - start_time) * 1000, 2)
        res["is_deepfake"] = (res.get("risk_band") == "high")
        return res
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

@router.post("/transcribe", status_code=status.HTTP_200_OK)
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """Transcribes call audio file (.ogg, .mp3, .wav, etc.) to text using Whisper."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext and ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed audio formats: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
        )
    
    start_time = time.time()
    temp_dir = tempfile.mkdtemp()
    filename = file.filename or "recording.ogg"
    temp_path = os.path.join(temp_dir, f"upload_{filename}")
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        transcript = transcribe_audio(temp_path)
        proc_time = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "success",
            "transcript": transcript,
            "filename": filename,
            "processing_time_ms": proc_time
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
