# ml/module2/predict.py
"""Public interface for Module 2: Scam Call Interceptor & Digital Arrest Detection."""

from rakshagrid.common.exceptions.base import MLInferenceException
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_scam.preprocessing.text_processor import extract_features, compute_rules_score
from rakshagrid.ai_scam.model.rules import score_lexicon
from rakshagrid.ai_scam.model.tfidf import get_scam_probability as tfidf_prob_fn
from rakshagrid.ai_scam.model.transformer import get_scam_probability as trans_prob_fn
from rakshagrid.ai_scam.model.ensemble import score_ensemble
from rakshagrid.ai_scam.model.llm_fallback import score_llm
from rakshagrid.ai_scam.model.audio import transcribe_audio
from rakshagrid.ai_scam.postprocessing.risk_calculator import format_verdict

logger = setup_logger("rakshagrid.ai_scam.predict")

def predict(transcript: str) -> dict:
    """
    Analyzes a call transcript through the full feature-augmented stacked ensemble.
    Falls back to LLM ONLY if the ensemble flags the call as needs_review.
    
    Args:
        transcript (str): The transcript text of the call/message.
        
    Returns:
        dict: Complete structured verdict payload.
    """
    text = transcript.strip()
    if not text:
        raise ValueError("Transcript text cannot be empty.")

    try:
        # 1. Layer A: Fast rules/lexicon scorer
        rules_res = score_lexicon(text)
        rules_score = compute_rules_score(rules_res)
        fired_features = [f["feature"] for f in rules_res.get("fired", [])]
        fired_features_detail = rules_res.get("fired", [])

        # 2. Layer B: Extract 9 engineered features
        eng_feats = extract_features(text)

        # 3. Layer C: TF-IDF + LogReg scam probability
        tfidf_prob = tfidf_prob_fn(text)

        # 4. Layer D: Fine-tuned Transformer scam probability
        trans_prob = trans_prob_fn(text)

        # 5. Layer E: Stacking ensemble meta-classifier
        ensemble_res = score_ensemble(tfidf_prob, trans_prob, rules_score, eng_feats)
        final_score = ensemble_res["score"]
        final_band = ensemble_res["band"]
        stage = ensemble_res["method"]

        # Rules Safety Override: if rules layer fires hard (>= 0.30) but ensemble is "low", force to needs_review
        if rules_score >= 0.30 and final_band == "low":
            final_band = "needs_review"
            stage = "rules_safety_override"

        # Route self-referential queries to LLM fallback
        text_lower = text.lower()
        is_self_referential = (
            "is it a scam" in text_lower or
            "is it safe" in text_lower or
            "is this a scam" in text_lower
        )

        llm_res = None
        # 6. Layer F: LLM fallback for borderline / needs_review cases
        if final_band == "needs_review" or is_self_referential:
            llm_res = score_llm(text)
            if llm_res.get("risk_band") in ["high", "low"]:
                final_band = llm_res["risk_band"]
                final_score = llm_res.get("score", final_score)
                stage = "llm_fallback"
            else:
                final_band = "needs_review"
                stage = llm_res.get("method", "llm_fallback_uncertain")
                final_score = llm_res.get("score", final_score)

        component_scores = {
            "rules": float(rules_score),
            "tfidf": float(tfidf_prob),
            "transformer": float(trans_prob),
            "ensemble": float(ensemble_res["score"])
        }
        if llm_res and "score" in llm_res:
            component_scores["llm_fallback"] = float(llm_res["score"])

        return format_verdict(
            stage=stage,
            final_score=final_score,
            final_band=final_band,
            fired_features=fired_features,
            fired_features_detail=fired_features_detail,
            component_scores=component_scores,
            eng_feats=eng_feats,
            transcript=text,
            llm_res=llm_res
        )
    except Exception as e:
        logger.error(f"Prediction error in module2: {e}")
        raise MLInferenceException(message=str(e), module_name="module2")


def predict_audio(audio_path: str) -> dict:
    """
    Transcribes call audio using Whisper and runs the text classification pipeline.
    """
    try:
        transcript = transcribe_audio(audio_path)
        if not transcript.strip() or transcript.startswith("[Audio transcription"):
            raise ValueError(f"Audio transcription failed: {transcript}")
        verdict = predict(transcript)
        verdict["transcript"] = transcript
        return verdict
    except Exception as e:
        logger.error(f"Audio prediction error in module2: {e}")
        raise MLInferenceException(message=str(e), module_name="module2")


def stream_predict(transcript_chunks: list) -> list:
    """
    Generates streaming payload items for transcript chunks.
    """
    results = []
    running_text = ""
    for chunk in transcript_chunks:
        running_text += " " + chunk.strip()
        rules_res = score_lexicon(running_text)
        payload = {
            "elapsed_chars": len(running_text),
            "risk_score": rules_res["score"],
            "risk_band": rules_res["band"],
            "fired_features": [f["feature"] for f in rules_res.get("fired", [])],
            "fired_details": rules_res.get("fired", [])
        }
        results.append(payload)
    return results
