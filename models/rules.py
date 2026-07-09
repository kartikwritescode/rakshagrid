# models/rules.py
import re
from typing import List, Dict

LEXICON = {
    "authority_impersonation": {
        "patterns": [r"\b(cbi|ed|customs|income tax dept|cyber cell)\b", r"\bwarrant\b", r"\bfir\b"],
        "weight": 0.30,
    },
    "isolation_secrecy": {
        "patterns": [r"don'?t (disconnect|hang up|tell anyone)", r"stay on (the )?call", r"video verification"],
        "weight": 0.25,
    },
    "urgency": {
        "patterns": [r"immediately", r"within (the next )?\d+ (minutes|hours)", r"right now"],
        "weight": 0.15,
    },
    "payment_channel_switch": {
        "patterns": [r"\bupi\b", r"gift card", r"crypto|bitcoin", r"transfer.*account"],
        "weight": 0.30,
    },
}

def score_lexicon(transcript: str) -> dict:
    text = transcript.lower()
    fired: List[Dict] = []
    score = 0.0

    for feature, cfg in LEXICON.items():
        matches = [m.group(0) for p in cfg["patterns"] if (m := re.search(p, text))]
        if matches:
            fired.append({"feature": feature, "weight": cfg["weight"], "matched": matches})
            score += cfg["weight"]

    score = min(score, 1.0)
    band = "high" if score > 0.6 else "medium" if score > 0.3 else "low"

    return {"score": score, "band": band, "fired": fired}