# models/llm_fallback.py
import os
import json
import config
from groq import Groq

_client = None

SYSTEM_PROMPT = """You are a scam-detection assistant. Given a call transcript, analyze it for potential scam/fraud indicators.
Look for: authority impersonation, urgency, isolation instructions, requests to switch payment channels (UPI/crypto/gift cards).

Respond ONLY with a valid JSON object matching this schema exactly:
{
  "is_scam": boolean,
  "confidence": number,
  "reasons": ["short phrase 1", "short phrase 2"],
  "risk_band": "high" or "low" or "needs_review"
}

Note: If you are not completely sure, set "risk_band" to "needs_review"."""

def _get_client():
    global _client
    if _client is None:
        api_key = config.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                _client = Groq(api_key=api_key)
            except Exception as e:
                print(f"Error initializing Groq client: {e}")
    return _client

def score_llm(transcript: str) -> dict:
    """
    Sends the transcript to Groq for classification fallback.
    Returns a dict with is_scam, confidence, reasons, risk_band, and method.
    """
    client = _get_client()
    if not client:
        return {
            "is_scam": False,
            "confidence": 0.5,
            "reasons": ["Groq client unavailable"],
            "risk_band": "needs_review",
            "method": "llm_fallback_unavailable"
        }

    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
            timeout=10.0  # 10s timeout to prevent hanging
        )
        
        result = json.loads(response.choices[0].message.content)
        result["method"] = "llm_fallback"
        
        # Verify the structure and normalize score
        is_scam = bool(result.get("is_scam", False))
        confidence = float(result.get("confidence", 0.5))
        
        # Calculate a standardized risk score:
        # If is_scam is True, risk_score is the confidence.
        # If is_scam is False, risk_score is 1 - confidence.
        score = confidence if is_scam else (1.0 - confidence)
        result["score"] = round(score, 3)
        
        if "risk_band" not in result:
            from utils.helpers import get_risk_band
            result["risk_band"] = get_risk_band(score)
            
        return result

    except Exception as e:
        print(f"Groq API call or parsing failed: {e}")
        return {
            "is_scam": False,
            "confidence": 0.5,
            "score": 0.5,
            "reasons": [f"LLM fallback error: {str(e)}"],
            "risk_band": "needs_review",
            "method": "llm_fallback_error"
        }