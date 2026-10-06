# packages/ai-currency/rakshagrid/ai_currency/predict.py
"""Public inference entrypoint for Module 1: Counterfeit Currency Detection."""

from packages.ai-currency.src.service import predict, currency_service

__all__ = ["predict", "currency_service"]
