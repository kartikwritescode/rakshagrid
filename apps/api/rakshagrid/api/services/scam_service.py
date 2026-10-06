# apps/api/src/services/scam_service.py
"""Service layer for Module 2 Scam Detection."""

from rakshagrid.ai_scam.predict import (
    predict as scam_predict,
    predict_audio as scam_predict_audio,
    stream_predict as scam_stream_predict
)

class ScamService:
    @staticmethod
    def analyze_text(transcript: str) -> dict:
        return scam_predict(transcript)

    @staticmethod
    def analyze_audio(file_path: str) -> dict:
        return scam_predict_audio(file_path)

    @staticmethod
    def analyze_stream(chunks: list[str]) -> list[dict]:
        return scam_stream_predict(chunks)

scam_service = ScamService()
