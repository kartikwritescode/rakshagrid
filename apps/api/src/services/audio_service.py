# apps/api/src/services/audio_service.py
"""
Service layer for audio processing, Whisper transcription, and scam call interception.

Architectural Design:
Audio
  │
  ├──> Speech-to-Text (Whisper)
  │       │
  │       └──> Text Scam Classifier (Stacked Ensemble)
  │
  └──> Acoustic Voice Deepfake Detector (RawNet2 / AASIST / Wav2Vec2)

Strictly separates voice biometrics from linguistic scam analysis:
- Scam risk band does NOT dictate deepfake status.
- Text content is never used as a proxy for acoustic voice synthesis.
- STT failure leaves voice analysis independent and never fabricates transcripts.
"""

import os
import shutil
import tempfile
import time
from rakshagrid.common.exceptions.base import (
    ValidationException,
    MLInferenceException,
    AudioTranscriptionException,
    MissingModelArtifactError,
)
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_scam.model.audio import transcribe_audio
from rakshagrid.ai_scam.model.voice_deepfake import (
    voice_deepfake_detector,
    VoiceDeepfakeDetector,
    VoiceDeepfakeStatus,
    VoiceDeepfakeResult,
)
from rakshagrid.ai_scam.predict import predict

logger = setup_logger("rakshagrid.api.audio_service")

ALLOWED_AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".ogg", ".opus", ".m4a", ".aac", ".flac", ".webm", ".wma", ".mp4"
}


class AudioService:
    """Encapsulates file persistence, validation, and invocation for audio processing."""

    def __init__(self, deepfake_detector: VoiceDeepfakeDetector = None):
        self.voice_detector = deepfake_detector or voice_deepfake_detector

    def validate_audio_file(self, filename: str):
        """Validates that file extension is supported."""
        ext = os.path.splitext(filename or "")[1].lower()
        if not ext or ext not in ALLOWED_AUDIO_EXTENSIONS:
            raise ValidationException(
                f"Unsupported audio format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
            )

    def detect_deepfake(self, file_obj, filename: str) -> dict:
        """
        Processes audio through parallel independent channels:
        1. Acoustic Voice Deepfake Detector (analyzes raw acoustic properties)
        2. Speech-to-Text (Whisper transcription)
           -> Text Scam Classifier (Stacked Ensemble)

        Scam risk (high/low) NEVER implies synthetic voice (deepfake/genuine).
        If acoustic model is unavailable, reports voice_analysis.status = 'unavailable'.
        """
        self.validate_audio_file(filename)
        start_time = time.perf_counter()

        clean_name = os.path.basename(filename or "recording.ogg").replace("/", "").replace("\\", "")
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, f"audio_{clean_name}")
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file_obj, buffer)

            # Channel 1: Independent Acoustic Voice Deepfake Detection
            voice_result = self.voice_detector.detect(temp_path)
            voice_analysis = voice_result.to_dict()

            # Channel 2: Speech-to-Text & Text Scam Classification
            transcription = None
            scam_analysis = None
            status = "success"
            scam_verdict = None

            try:
                transcript_text = transcribe_audio(temp_path)
                transcription = {
                    "status": "success",
                    "transcript": transcript_text,
                    "reason_code": None,
                    "message": "Audio transcribed successfully.",
                    "model": "whisper",
                }

                # Linguistic Scam Classification on transcript
                scam_verdict = predict(transcript_text)
                scam_analysis = {
                    "status": "success",
                    "is_scam": (scam_verdict["risk_band"] == "high"),
                    "risk_score": scam_verdict["risk_score"],
                    "risk_band": scam_verdict["risk_band"],
                    "stage": scam_verdict["stage"],
                    "fired_features": scam_verdict.get("fired_features", []),
                    "component_scores": scam_verdict.get("component_scores", {}),
                    "reason": None,
                }
            except AudioTranscriptionException as stt_err:
                logger.warning(f"Audio transcription failed for '{filename}': {stt_err.reason_code}")
                status = "transcription_failed"
                transcription = {
                    "status": "failed",
                    "transcript": None,
                    "reason_code": stt_err.reason_code,
                    "message": stt_err.message,
                    "model": "whisper",
                }
                scam_analysis = {
                    "status": "not_analyzed",
                    "is_scam": None,
                    "risk_score": None,
                    "risk_band": None,
                    "stage": "stt_failure",
                    "fired_features": [],
                    "component_scores": {},
                    "reason": f"Scam classification requires transcript; STT failed ({stt_err.reason_code}).",
                }

            proc_time = round((time.perf_counter() - start_time) * 1000, 2)

            # Assemble clean decoupled response
            return {
                "status": status,
                "filename": filename,
                "transcription": transcription,
                "scam_analysis": scam_analysis,
                "voice_analysis": voice_analysis,
                "processing_time_ms": proc_time,
                # Backward compatibility mirrors:
                "stt_status": transcription["status"],
                "transcript": transcription["transcript"],
                "reason_code": transcription["reason_code"],
                "message": transcription["message"],
                "is_scam": scam_analysis.get("is_scam") if scam_analysis else None,
                "risk_score": scam_analysis.get("risk_score") if scam_analysis else None,
                "risk_band": scam_analysis.get("risk_band") if scam_analysis else None,
                "stage": scam_analysis.get("stage") if scam_analysis else None,
                "scam_classification": {
                    "risk_score": scam_analysis.get("risk_score"),
                    "risk_band": scam_analysis.get("risk_band"),
                    "stage": scam_analysis.get("stage"),
                    "fired_features": scam_analysis.get("fired_features", []),
                    "component_scores": scam_analysis.get("component_scores", {}),
                } if scam_verdict else None,
                "llm_fallback": {
                    "invoked": scam_verdict.get("stage") == "llm_fallback" if scam_verdict else False,
                    "method": scam_verdict.get("stage") if scam_verdict else "not_invoked",
                } if scam_verdict else None,
                "voice_deepfake_detection": voice_analysis,
            }
        except (ValidationException, AudioTranscriptionException, MissingModelArtifactError):
            raise
        except Exception as e:
            logger.error(f"Unexpected audio detection failure: {e}")
            raise MLInferenceException(f"Audio analysis failed: {e}", module_name="ai-scam")
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            if os.path.exists(temp_dir):
                try:
                    os.rmdir(temp_dir)
                except OSError:
                    pass

    def transcribe(self, file_obj, filename: str) -> dict:
        """
        Transcribes audio file to text using Whisper.
        Returns structured failure state if STT fails without fabricating text.
        """
        self.validate_audio_file(filename)
        start_time = time.perf_counter()

        clean_name = os.path.basename(filename or "recording.ogg").replace("/", "").replace("\\", "")
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, f"transcribe_{clean_name}")
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file_obj, buffer)

            transcript = transcribe_audio(temp_path)
            proc_time = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "success",
                "transcript": transcript,
                "reason_code": None,
                "message": "Audio transcribed successfully.",
                "filename": filename,
                "model": "whisper",
                "processing_time_ms": proc_time,
            }
        except AudioTranscriptionException as stt_err:
            proc_time = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning(f"Audio transcription failed for '{filename}': {stt_err.reason_code}")
            return {
                "status": "transcription_failed",
                "reason_code": stt_err.reason_code,
                "message": stt_err.message,
                "transcript": None,
                "filename": filename,
                "model": "whisper",
                "processing_time_ms": proc_time,
            }
        except (ValidationException, MissingModelArtifactError):
            raise
        except Exception as e:
            logger.error(f"Unexpected audio transcription failure: {e}")
            raise MLInferenceException(f"Audio transcription failed: {e}", module_name="ai-scam")
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            if os.path.exists(temp_dir):
                try:
                    os.rmdir(temp_dir)
                except OSError:
                    pass


audio_service = AudioService()
