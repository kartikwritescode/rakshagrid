# apps/api/src/schemas/error_schema.py
"""Structured standard error response schema."""

from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    error: bool = True
    code: str = Field(..., description="Machine-readable error code, e.g. VALIDATION_ERROR, NOT_FOUND, INTERNAL_ERROR")
    message: str = Field(..., description="Safe human-readable error description")
    request_id: str | None = Field(default=None, description="Unique trace request ID")
    details: dict | None = Field(default=None, description="Safe contextual metadata")
