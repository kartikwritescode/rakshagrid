# models/llm_fallback.py
import os
import json
import config
from groq import Groq

_client = None

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
    global _client
    if _client is None:
        api_key = config.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if not api_key:
            print("\n" + "!" * 80)
            print("!!! WARNING: GROQ_API_KEY IS NOT SET IN ENVIRONMENT OR .ENV !!!")
            print("!!! LLM FALLBACK FOR SCAM DETECTION WILL BE COMPLETELY UNAVAILABLE !!!")
            print("!" * 80 + "\n")
        else:
            try:
                _client = Groq(api_key=api_key)
                print("\n=== Groq Client Initialized Successfully ===")
            except Exception as e:
                print("\n" + "!" * 80)
                print(f"!!! CRITICAL ERROR: GROQ CLIENT INITIALIZATION FAILED: {e} !!!")
                print("!!!" + " " * 74 + "!!!")
                print("!!! PLEASE CHECK YOUR GROQ SDK AND HTTPX COMPATIBILITY !!!")
                print("!" * 80 + "\n")
    return _client

# Initialize client eagerly at import time
_get_client()

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
        
        # Bug B Fix: Force needs_review if LLM confidence is low
        if confidence < 0.70:
            result["risk_band"] = "needs_review"
            
        # Bug A Fix: Calculate a standardized risk score correctly:
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