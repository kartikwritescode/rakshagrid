# models/audio.py
import torch
import config
from faster_whisper import WhisperModel

_model = None

def _load_model():
    global _model
    if _model is None:
        try:
            device = config.WHISPER_DEVICE
            compute_type = config.WHISPER_COMPUTE_TYPE
            
            # CPU fallback if CUDA requested but not available
            if "cuda" in device and not torch.cuda.is_available():
                print("CUDA not available. Whisper falling back to CPU.")
                device = "cpu"
                compute_type = "int8"
                
            _model = WhisperModel(
                config.WHISPER_MODEL_SIZE,
                device=device,
                compute_type=compute_type
            )
        except Exception as e:
            print(f"Error loading Whisper model: {e}")

def transcribe_audio(file_path: str) -> str:
    """Transcribes an audio file into text using faster-whisper."""
    _load_model()
    if _model is None:
        return "[Audio transcription unavailable: Whisper model failed to load]"
    try:
        segments, _ = _model.transcribe(file_path)
        text = " ".join(seg.text for seg in segments)
        return text.strip()
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        return f"[Audio transcription error: {str(e)}]"