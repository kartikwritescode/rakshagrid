# ml/module2/postprocessing/risk_calculator.py
"""Postprocessing and formatting for scam analysis results."""

def format_verdict(
    stage: str,
    final_score: float,
    final_band: str,
    fired_features: list,
    fired_features_detail: list,
    component_scores: dict,
    eng_feats: dict,
    transcript: str,
    llm_res: dict | None = None
) -> dict:
    """Formats raw components into standardized verdict payload."""
    breakdown = {
        "engineered_features": eng_feats,
        "rules_detail": fired_features_detail
    }
    if llm_res:
        breakdown["llm_analysis"] = llm_res.get("analysis", "")
        breakdown["llm_reasons"] = llm_res.get("reasons", [])

    return {
        "stage": stage,
        "risk_score": round(final_score, 4),
        "risk_band": final_band,
        "fired_features": fired_features,
        "fired_features_detail": fired_features_detail,
        "component_scores": component_scores,
        "breakdown": breakdown,
        "transcript": transcript
    }
