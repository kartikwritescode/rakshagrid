# packages/ai-scam/rakshagrid/ai_scam/predict.py
"""Public interface for Module 2: Scam Call Interceptor & Digital Arrest Detection."""

from rakshagrid.common.exceptions.base import (
    MLInferenceException,
    ValidationException,
    AudioTranscriptionException,
)
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_scam.config import scam_config
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
    if not isinstance(transcript, str) or not transcript.strip():
        raise ValidationException("Transcript text cannot be empty.")

    text = transcript.strip()

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

        # Rules Safety Override: Centralized threshold
        if rules_score >= scam_config.RULES_SAFETY_OVERRIDE_THRESHOLD and final_band == "low":
            final_band = "needs_review"
            stage = "rules_safety_override"

        # Route self-referential queries to LLM fallback
        text_lower = text.lower()
        is_self_referential = (
            "is it a scam" in text_lower
            or "is it safe" in text_lower
            or "is this a scam" in text_lower
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
            "ensemble": float(ensemble_res["score"]),
        }
        if llm_res and "score" in llm_res:
            component_scores["llm_fallback"] = float(llm_res["score"])

        verdict = format_verdict(
            stage=stage,
            final_score=final_score,
            final_band=final_band,
            fired_features=fired_features,
            fired_features_detail=fired_features_detail,
            component_scores=component_scores,
            eng_feats=eng_feats,
            transcript=text,
            llm_res=llm_res,
        )
        verdict["stt_status"] = "not_applicable"
        return verdict
    except (ValidationException, AudioTranscriptionException):
        raise
    except Exception as e:
        logger.error(f"Prediction error in ai-scam: {e}")
        raise MLInferenceException(message=str(e), module_name="ai-scam")


def predict_audio(audio_path: str) -> dict:
    """
    Transcribes call audio using Whisper and runs the text classification pipeline.
    Preserves AudioTranscriptionException when STT fails; never fabricates transcripts.
    """
    # 1. Genuinely transcribe audio; raises AudioTranscriptionException if STT fails
    transcript = transcribe_audio(audio_path)
    if not transcript or not transcript.strip():
        raise AudioTranscriptionException(
            message="Audio transcription returned an empty transcript.",
            reason_code="EMPTY_TRANSCRIPT",
        )

    # 2. Score real transcript
    verdict = predict(transcript)
    verdict["transcript"] = transcript
    verdict["stt_status"] = "success"
    return verdict


def evaluate_stream_chunk(running_text: str) -> dict:
    """Evaluates incremental text for streaming analysis."""
    rules_res = score_lexicon(running_text)
    return {
        "elapsed_chars": len(running_text),
        "risk_score": round(rules_res["score"], 4),
        "risk_band": rules_res["band"],
        "fired_features": [f["feature"] for f in rules_res.get("fired", [])],
        "fired_details": rules_res.get("fired", []),
    }


def stream_predict(transcript_chunks: list[str]) -> list[dict]:
    """Generates sequential evaluations for transcript chunks."""
    results = []
    running_text = ""
    for chunk in transcript_chunks:
        running_text += (" " if running_text else "") + chunk.strip()
        results.append(evaluate_stream_chunk(running_text))
    return results
