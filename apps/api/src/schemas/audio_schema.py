# apps/api/src/schemas/audio_schema.py
"""
Schemas for audio processing, transcription, and detection endpoints.

Enforces clear separation between:
1. Speech-to-text transcription
2. Linguistic scam analysis
3. Acoustic voice deepfake detection
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TranscribeResponse(BaseModel):
    """Payload returned by /api/v1/audio/transcribe."""
    status: str = Field(..., description="'success' or 'transcription_failed'")
    transcript: Optional[str] = Field(default=None, description="Transcribed text string")
    reason_code: Optional[str] = Field(default=None, description="Failure code if STT failed")
    message: Optional[str] = Field(default=None, description="Informative status message")
    filename: Optional[str] = None
    model: Optional[str] = Field(default="whisper", description="Speech-to-text model name")
    processing_time_ms: Optional[float] = None


class TranscriptionResult(BaseModel):
    """Structured transcription output within audio detection."""
    status: str = Field(..., description="'success' or 'failed'")
    transcript: Optional[str] = Field(default=None, description="Transcribed audio contents")
    reason_code: Optional[str] = Field(default=None, description="Failure code if STT failed")
    message: Optional[str] = Field(default=None, description="Informative status message")
    model: Optional[str] = Field(default="whisper", description="Speech-to-text model name")


class ScamAnalysisResult(BaseModel):
    """Structured linguistic scam analysis from transcript text."""
    status: str = Field(..., description="'success', 'not_analyzed', or 'failed'")
    is_scam: Optional[bool] = Field(default=None, description="Scam call flag")
    risk_score: Optional[float] = Field(default=None, description="Scam probability score [0.0 - 1.0]")
    risk_band: Optional[str] = Field(default=None, description="'low', 'needs_review', 'high'")
    stage: Optional[str] = Field(default=None, description="Interception stage (e.g. ensemble_stacking)")
    fired_features: Optional[List[str]] = Field(default=None, description="Features flagged by rules/lexicon")
    component_scores: Optional[Dict[str, float]] = Field(default=None, description="Scores per pipeline component")
    reason: Optional[str] = Field(default=None, description="Explanation if scam analysis was bypassed/failed")


class VoiceAnalysisResult(BaseModel):
    """
    Structured acoustic voice deepfake detection.
    
    Status can be:
    - 'detected' (synthetic voice detected via acoustic model)
    - 'not_detected' (natural voice confirmed via acoustic model)
    - 'unavailable' (no acoustic model weights available)
    - 'insufficient_quality' (audio file too short or corrupted)
    - 'processing_error' (error during acoustic feature extraction)
    """
    status: str = Field(..., description="'detected', 'not_detected', 'unavailable', 'insufficient_quality', 'processing_error'")
    is_deepfake: Optional[bool] = Field(default=None, description="Synthetic voice flag (None if unavailable/error)")
    confidence: Optional[float] = Field(default=None, description="Acoustic spoofing confidence score [0.0 - 1.0]")
    model_name: Optional[str] = Field(default=None, description="Acoustic model architecture (e.g. RawNet2, AASIST)")
    reason: Optional[str] = Field(default=None, description="Explanation of status or absence of model")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Acoustic diagnostic details")


class AudioDetectResponse(BaseModel):
    """
    Payload returned by /api/v1/audio/detect.
    
    Maintains clean separation between transcription, scam analysis, and voice deepfake analysis.
    """
    status: str = Field(..., description="'success', 'transcription_failed', or 'partial'")
    filename: Optional[str] = None
    transcription: TranscriptionResult
    scam_analysis: Optional[ScamAnalysisResult] = None
    voice_analysis: VoiceAnalysisResult
    processing_time_ms: Optional[float] = None

    # Backward-compatible convenience fields:
    stt_status: Optional[str] = Field(default=None, description="Convenience mirror of transcription.status")
    transcript: Optional[str] = Field(default=None, description="Convenience mirror of transcription.transcript")
    reason_code: Optional[str] = Field(default=None, description="Convenience mirror of transcription.reason_code")
    message: Optional[str] = Field(default=None, description="Convenience mirror of transcription.message")
    is_scam: Optional[bool] = Field(default=None, description="Convenience mirror of scam_analysis.is_scam")
    risk_score: Optional[float] = Field(default=None, description="Convenience mirror of scam_analysis.risk_score")
    risk_band: Optional[str] = Field(default=None, description="Convenience mirror of scam_analysis.risk_band")
    stage: Optional[str] = Field(default=None, description="Convenience mirror of scam_analysis.stage")
    scam_classification: Optional[Dict[str, Any]] = Field(default=None, description="Backward-compatible details")
    llm_fallback: Optional[Dict[str, Any]] = Field(default=None, description="Backward-compatible LLM fallback details")
    voice_deepfake_detection: Optional[Dict[str, Any]] = Field(default=None, description="Backward-compatible mirror of voice_analysis")
