# backend/fastapi/app/services/scam_service.py
"""Service layer for Module 2 Scam Detection."""

from ml.module2 import predict as scam_predict

class ScamService:
    @staticmethod
    def analyze_text(transcript: str) -> dict:
        return scam_predict.predict(transcript)

    @staticmethod
    def analyze_audio(file_path: str) -> dict:
        return scam_predict.predict_audio(file_path)

    @staticmethod
    def analyze_stream(chunks: list[str]) -> list[dict]:
        return scam_predict.stream_predict(chunks)

scam_service = ScamService()
