# backend/fastapi/app/services/currency_service.py
"""Service layer for Module 1 Currency Counterfeit Detection."""

from ml.module1_currency import predict as currency_predict

class CurrencyService:
    @staticmethod
    def analyze_image(image_bytes: bytes) -> dict:
        return currency_predict.predict(image_bytes)

currency_service = CurrencyService()
