# packages/ai-scam/rakshagrid/ai_scam/model/audio.py
"""
Robust Audio Transcription Engine for Call Recordings (.wav, .mp3, .ogg, .m4a, .flac, .webm).

Prioritizes actual Whisper transcription (Faster-Whisper -> OpenAI Whisper -> Groq Cloud Whisper).
Strictly eliminates deceptive hardcoded fallback transcripts.
Raises AudioTranscriptionException if transcription cannot be genuinely completed.
"""

import os
from rakshagrid.common.exceptions.base import AudioTranscriptionException
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_scam.config import scam_config

logger = setup_logger("rakshagrid.ai_scam.audio")

_whisper_model = None
_whisper_backend = None


def _load_whisper():
    """Lazily loads local Faster-Whisper or OpenAI Whisper model."""
    global _whisper_model, _whisper_backend
    if _whisper_model is not None:
        return _whisper_model

    # Tier 1: Try faster-whisper
    try:
        from faster_whisper import WhisperModel
        device = scam_config.get_whisper_device()
        compute_type = "int8" if device == "cpu" else "float16"
        model_size = scam_config.WHISPER_MODEL_SIZE
        _whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        _whisper_backend = "faster-whisper"
        logger.info(f"Initialized Faster-Whisper ({model_size}) on {device}")
        return _whisper_model
    except Exception as e1:
        logger.debug(f"Faster-Whisper initialization failed: {e1}. Trying OpenAI Whisper...")

    # Tier 2: Try openai-whisper
    try:
        import whisper
        model_size = scam_config.WHISPER_MODEL_SIZE
        _whisper_model = whisper.load_model(model_size)
        _whisper_backend = "openai-whisper"
        logger.info(f"Initialized OpenAI Whisper ({model_size})")
        return _whisper_model
    except Exception as e2:
        logger.debug(f"OpenAI Whisper initialization failed: {e2}")
        _whisper_model = None
        _whisper_backend = None

    return _whisper_model


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes call audio file (.wav, .mp3, .ogg, .m4a, .flac, .webm).
    Uses Faster-Whisper -> OpenAI Whisper -> Groq Cloud Audio Whisper.
    
    Returns genuine transcription string or raises AudioTranscriptionException.
    NEVER fabricates a simulated transcript.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    last_error = None

    # Tier 1 & 2: Local Whisper models
    model = _load_whisper()
    if model is not None:
        try:
            if hasattr(model, "transcribe"):
                # faster-whisper returns (segments, info) generator
                res = model.transcribe(audio_path, beam_size=5)
                if isinstance(res, tuple):
                    segments, info = res
                    transcript_parts = [segment.text.strip() for segment in segments]
                    full_text = " ".join(transcript_parts).strip()
                elif isinstance(res, dict):
                    full_text = res.get("text", "").strip()
                else:
                    full_text = str(res).strip()

                if full_text:
                    return full_text
                else:
                    raise AudioTranscriptionException(
                        message="Audio file processed successfully but contained no intelligible speech.",
                        reason_code="EMPTY_TRANSCRIPT",
                    )
        except AudioTranscriptionException:
            raise
        except Exception as e:
            logger.warning(f"Local Whisper transcription failed: {e}. Attempting cloud fallback...")
            last_error = e

    # Tier 3: Groq Cloud Audio Whisper API
    api_key = scam_config.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            with open(audio_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(audio_path), file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                    temperature=0.0,
                )
                text = transcription.text.strip()
                if text:
                    return text
                else:
                    raise AudioTranscriptionException(
                        message="Cloud STT completed but returned an empty transcript.",
                        reason_code="EMPTY_TRANSCRIPT",
                    )
        except AudioTranscriptionException:
            raise
        except Exception as e:
            logger.warning(f"Groq Audio API transcription failed: {e}")
            last_error = e

    # STT completely unavailable or failed: Raise domain exception with explicit reason code
    err_detail = f": {last_error}" if last_error else ""
    logger.error(f"Audio transcription failed for '{os.path.basename(audio_path)}'{err_detail}")
    raise AudioTranscriptionException(
        message="Audio transcription service is unavailable or speech could not be processed.",
        reason_code="TRANSCRIPTION_SERVICE_UNAVAILABLE",
        status_code=503,
    )
