# backend/fastapi/app/services/crime_service.py
"""Service layer for Module 4 VigilGrid Crime Intelligence."""

from rakshagrid.ai_crime import predict as crime_predict

class CrimeService:
    @staticmethod
    def get_hotspots() -> list[dict]:
        return crime_predict.predict_hotspots()

    @staticmethod
    def get_points(limit: int = 5000) -> list[dict]:
        return crime_predict.predict_points(limit=limit)

    @staticmethod
    def allocate_patrols(n_units: int = 10) -> list[dict]:
        return crime_predict.allocate_patrols(n_units=n_units)

    @staticmethod
    def get_status() -> dict:
        return crime_predict.get_engine_status()

crime_service = CrimeService()
