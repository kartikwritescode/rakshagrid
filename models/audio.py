# models/audio.py
from faster_whisper import WhisperModel

_model = WhisperModel("base", device="cuda", compute_type="int8")   # use "cuda" if you have a GPU

def transcribe_audio(file_path: str) -> str:
    segments, _ = _model.transcribe(file_path)
    return " ".join(seg.text for seg in segments)