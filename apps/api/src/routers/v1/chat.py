# apps/api/src/routers/v1/chat.py
"""Router for FraudShield citizen AI safety chat advisor."""

from fastapi import APIRouter, Depends, status
from apps.api.src.core.security import verify_api_key
from apps.api.src.schemas.chat_schema import ChatRequest, ChatResponse
from apps.api.src.services.scam_service import scam_service

router = APIRouter(
    prefix="/chat",
    tags=["FraudShield AI Advisor"],
    dependencies=[Depends(verify_api_key)],
)

@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def fraudshield_chat(payload: ChatRequest):
    """Provides interactive safety guidance and real-time risk assessment for citizens."""
    full_text = payload.transcript or ""
    if not full_text and payload.messages:
        user_msgs = [m.content for m in payload.messages if m.role == "user"]
        full_text = " ".join(user_msgs)

    risk_score = 0.1
    risk_band = "low"
    flagged = []
    
    if full_text.strip():
        try:
            verdict = scam_service.analyze_text(full_text)
            risk_score = verdict.get("risk_score", 0.1)
            risk_band = verdict.get("risk_band", "low")
            flagged = verdict.get("fired_features", [])
        except Exception:
            pass

    if risk_band == "high":
        reply = (
            "🚨 CRITICAL ALERT: The conversation or message you shared exhibits severe indicators of an active scam or digital arrest coercion. "
            "Do NOT transfer funds, do NOT share OTPs or credentials, and immediately sever contact with the caller."
        )
        action = "Hang up immediately, lock banking credentials, and dial 1930 to report to the National Cyber Crime Portal."
    elif risk_band == "needs_review":
        reply = (
            "⚠️ CAUTION: Suspicious patterns were detected in this conversation. "
            "Legitimate government or banking officials will never demand immediate money transfers over the phone or demand secrecy."
        )
        action = "Verify the caller's identity through official public channels before taking any action."
    else:
        reply = (
            "✅ Analysis indicates low scam risk based on the provided text. "
            "Continue exercising standard digital vigilance and never share one-time passwords."
        )
        action = "No immediate threat detected. Keep safety guidelines in mind."

    return ChatResponse(
        reply=reply,
        risk_score=risk_score,
        risk_band=risk_band,
        flagged_indicators=flagged,
        recommended_action=action
    )
