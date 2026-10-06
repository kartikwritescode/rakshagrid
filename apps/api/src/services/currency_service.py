# apps/api/src/services/currency_service.py
"""Service layer for Module 1 Currency Counterfeit Detection."""

from rakshagrid.ai_currency.service import currency_service as ai_currency_svc

class CurrencyService:
    @staticmethod
    def analyze_image(image_bytes: bytes, filename: str | None = None, content_type: str = "image/jpeg") -> dict:
        return ai_currency_svc.analyze_image(
            image_bytes=image_bytes,
            filename=filename,
            content_type=content_type
        )

currency_service = CurrencyService()

