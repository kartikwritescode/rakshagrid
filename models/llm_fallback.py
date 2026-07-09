# models/llm_fallback.py
import os, json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a scam-detection assistant. Given a call transcript, respond ONLY with valid JSON:
{"is_scam": boolean, "confidence": number between 0 and 1, "reasons": [short phrases]}
Look for: authority impersonation, urgency, isolation instructions, requests to switch payment channels (UPI/crypto/gift cards)."""

def score_llm(transcript: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)