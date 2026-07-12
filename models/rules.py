# models/rules.py
import re
from typing import List, Dict
from utils.helpers import get_risk_band

from utils.scam_lexicon import LEXICON


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
    band = get_risk_band(score)

    return {"score": score, "band": band, "fired": fired}