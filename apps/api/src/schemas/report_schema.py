# apps/api/src/schemas/report_schema.py
"""Schemas for citizen crime reporting and evidence intake."""

from pydantic import BaseModel, Field

class CrimeReportCreate(BaseModel):
    id: str | None = Field(default=None, description="Optional custom or client report identifier")
    victimName: str = Field(default="Anonymous Citizen", description="Reporting citizen or victim name")
    phoneNumber: str = Field(default="", description="Contact or scammer phone number")
    upiId: str = Field(default="", description="Scammer UPI handle")
    bankAccount: str = Field(default="", description="Scammer or beneficiary bank account")
    deviceFingerprint: str = Field(default="", description="Device fingerprint token")
    typeOfScam: str = Field(default="UPI Scam", description="Scam classification category")
    description: str = Field(default="", description="Detailed narrative of incident")
    amountLost: float = Field(default=0.0, description="Financial loss incurred in INR")
    city: str = Field(default="", description="Incident city location")
    state: str = Field(default="", description="Incident state")

class CrimeReport(CrimeReportCreate):
    id: str = Field(..., description="Unique report identifier, e.g. REP-89214")
    timestamp: str = Field(..., description="ISO 8601 formatted report timestamp")
    riskScore: float = Field(default=0.0, description="Evaluated scam risk score")
    riskBand: str = Field(default="low", description="Evaluated scam risk band")

class ReportListResponse(BaseModel):
    reports: list[CrimeReport] = Field(default_factory=list)
    total: int = 0
