# shared/exceptions/base.py
"""Centralized exception definitions for Raksha Grid platform."""

class RakshaGridException(Exception):
    """Base exception for all Raksha Grid application errors."""
    def __init__(self, message: str, status_code: int = 500, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class MLInferenceException(RakshaGridException):
    """Raised when an error occurs during ML model prediction or inference."""
    def __init__(self, message: str, module_name: str, details: dict | None = None):
        super().__init__(
            message=f"[{module_name}] Inference Error: {message}",
            status_code=500,
            details=details
        )
        self.module_name = module_name


class ValidationException(RakshaGridException):
    """Raised when request payload or input data fails validation."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, status_code=400, details=details)


class ResourceNotFoundException(RakshaGridException):
    """Raised when a requested resource or file is not found."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, status_code=404, details=details)
