# packages/common/rakshagrid/common/exceptions/base.py
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

    def __init__(self, message: str, module_name: str = "ml", details: dict | None = None):
        super().__init__(
            message=f"[{module_name}] Inference Error: {message}",
            status_code=500,
            details=details,
        )
        self.module_name = module_name


class MissingModelArtifactError(MLInferenceException):
    """Raised when a required machine learning model weight or artifact file is missing."""

    def __init__(self, message: str, module_name: str = "core", details: dict | None = None):
        super().__init__(
            message=f"Missing required model artifact: {message}",
            module_name=module_name,
            details=details,
        )


class ValidationException(RakshaGridException):
    """Raised when request payload or input data fails validation."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, status_code=400, details=details)


class ResourceNotFoundException(RakshaGridException):
    """Raised when a requested resource or file is not found."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, status_code=404, details=details)


class AudioTranscriptionException(RakshaGridException):
    """Raised when speech-to-text transcription fails or transcription service is unavailable."""

    def __init__(
        self,
        message: str = "Audio transcription service is unavailable",
        reason_code: str = "TRANSCRIPTION_SERVICE_UNAVAILABLE",
        status_code: int = 503,
        details: dict | None = None,
    ):
        det = details or {}
        det.setdefault("reason_code", reason_code)
        det.setdefault("status", "transcription_failed")
        super().__init__(message=message, status_code=status_code, details=det)
        self.reason_code = reason_code
        self.status = "transcription_failed"


class CrimeDataUnavailableException(RakshaGridException):
    """Raised when VigilGrid crime dataset is missing or unavailable."""

    def __init__(
        self,
        message: str = "VigilGrid crime dataset is not available at the configured location.",
        code: str = "CRIME_DATA_UNAVAILABLE",
        status_code: int = 503,
        details: dict | None = None,
    ):
        det = details or {}
        det.setdefault("code", code)
        det.setdefault("status", "data_unavailable")
        super().__init__(message=message, status_code=status_code, details=det)
        self.code = code
        self.status = "data_unavailable"

