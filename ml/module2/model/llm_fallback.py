# ml/module2/model/llm_fallback.py
"""Groq LLM Fallback Classifier for Borderline Cases."""

import os
import json
from ml.module2.config import scam_config

_client = None
_groq_available = None

SYSTEM_PROMPT = """You are a scam-detection assistant. Given a call transcript, analyze it for potential scam/fraud indicators.
Look for actual requests for money, OTPs, credentials, remote access (TeamViewer/AnyDesk), digital arrests, or legal/disconnection threats.

CRITICAL INSTRUCTIONS:
1. Do NOT flag a call as a scam if it only contains greetings, introductions, or generic cold-opens (e.g., "hello this is Alex from Microsoft", "DHL courier package for you") without any actual scam action, threat, or request. A simple introduction is NOT a scam.
2. If the text is very short or is just a greeting/introduction, classify it as "low" risk.
3. Set the "confidence" field to a float between 0.0 and 1.0 representing how confident you are in your classification choice (e.g., 1.0 if you are absolutely certain of your choice, 0.5 if you are highly uncertain).
4. If the call is a borderline case, a self-referential meta-discussion (e.g., a customer asking a friend or bank "is this link safe?", "did you send me this verification pin?"), or you are not completely sure, you MUST set "risk_band" to "needs_review" and set "confidence" to a lower value (e.g., 0.5 to 0.6). Do not classify such self-referential discussions of scams as a confident "low".

Respond ONLY with a valid JSON object matching this schema exactly:
{
  "is_scam": boolean,
  "confidence": number,
  "reasons": ["short phrase 1", "short phrase 2"],
  "risk_band": "high" or "low" or "needs_review"
}"""

def _get_client():
    global _client, _groq_available
    if _client is None:
        try:
            from groq import Groq
            _groq_available = True
        except ImportError:
            _groq_available = False
            print("[Warning] groq module not installed. LLM Fallback will use default fallback response.")
            return None

        api_key = scam_config.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if not api_key:
            print("WARNING: GROQ_API_KEY IS NOT SET IN ENVIRONMENT OR .ENV")
        else:
            try:
                _client = Groq(api_key=api_key)
                print("=== Groq Client Initialized Successfully ===")
            except Exception as e:
                print(f"CRITICAL ERROR: GROQ CLIENT INITIALIZATION FAILED: {e}")
    return _client

def score_llm(transcript: str) -> dict:
    """Sends transcript to Groq for classification fallback."""
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
            model=scam_config.GROQ_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
            timeout=10.0
        )
        
        result = json.loads(response.choices[0].message.content)
        result["method"] = "llm_fallback"
        
        is_scam = bool(result.get("is_scam", False))
        confidence = float(result.get("confidence", 0.5))
        
        if confidence < 0.70:
            result["risk_band"] = "needs_review"
            
        score = confidence if is_scam else (1.0 - confidence)
        result["score"] = round(score, 3)
        
        if "risk_band" not in result:
            from ml.module2.utils.helpers import get_risk_band
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
