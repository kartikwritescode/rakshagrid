# apps/api/src/routers/v1/reports.py
"""Router for citizen fraud report intake and registry."""

from fastapi import APIRouter, Depends, HTTPException, status
from apps.api.src.core.security import verify_api_key
from apps.api.src.schemas.report_schema import CrimeReportCreate, CrimeReport, ReportListResponse
from apps.api.src.services.graph_service import graph_service
from apps.api.src.services.scam_service import scam_service

router = APIRouter(
    prefix="/reports",
    tags=["Citizen Crime Reports"],
    dependencies=[Depends(verify_api_key)],
)

@router.post("", response_model=CrimeReport, status_code=status.HTTP_201_CREATED)
def submit_crime_report(payload: CrimeReportCreate):
    """Submits a citizen fraud report, automatically assessing scam risk and adding to the graph."""
    text_to_eval = f"{payload.typeOfScam}: {payload.description} Phone: {payload.phoneNumber} UPI: {payload.upiId}"
    risk_score = 0.5
    risk_band = "needs_review"
    
    if payload.description.strip():
        try:
            verdict = scam_service.analyze_text(text_to_eval)
            risk_score = verdict.get("risk_score", 0.5)
            risk_band = verdict.get("risk_band", "needs_review")
        except Exception:
            pass

    report_dict = payload.model_dump()
    report_dict["riskScore"] = risk_score
    report_dict["riskBand"] = risk_band

    created = graph_service.add_report(report_dict)
    return created

@router.get("", response_model=ReportListResponse, status_code=status.HTTP_200_OK)
def list_crime_reports():
    """Lists all registered fraud incidents."""
    reports = graph_service.get_reports()
    return {
        "reports": reports,
        "total": len(reports)
    }

@router.get("/{report_id}", response_model=CrimeReport, status_code=status.HTTP_200_OK)
def get_crime_report(report_id: str):
    """Retrieves a specific registered fraud report by unique identifier."""
    report = graph_service.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' was not found.",
        )
    return report
