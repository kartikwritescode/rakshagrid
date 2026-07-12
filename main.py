# main.py
import os
import json
import asyncio
import shutil
import tempfile
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import config
from schemas import TextRequest, StreamRequest, VerdictResponse
from utils.preprocessing import extract_features, compute_rules_score
from utils.helpers import get_risk_band

# Import our models
from models.rules import score_lexicon
from models.tfidf_model import score_tfidf, get_scam_probability as tfidf_prob_fn
from models.transformer_model import score_transformer, get_scam_probability as trans_prob_fn
from models.ensemble import score_ensemble
from models.llm_fallback import score_llm
from models.audio import transcribe_audio

app = FastAPI(title="Raksha Grid API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint showing model loading status."""
    import os
    tfidf_loaded = os.path.exists(config.TFIDF_MODEL_PATH)
    trans_loaded = os.path.exists(config.TRANSFORMER_MODEL_PATH)
    ensemble_loaded = os.path.exists(config.ENSEMBLE_MODEL_PATH)
    
    return {
        "status": "healthy",
        "service": "raksha-grid-api",
        "models_status": {
            "tfidf": "loaded" if tfidf_loaded else "not_trained",
            "transformer": "loaded" if trans_loaded else "not_trained",
            "ensemble": "loaded" if ensemble_loaded else "not_trained"
        }
    }

@app.post("/api/scam/analyze-text", response_model=VerdictResponse)
def analyze_text(req: TextRequest):
    """
    Analyzes a call transcript through the full feature-augmented stacked ensemble.
    Falls back to LLM ONLY if the ensemble flags the call as needs_review.
    """
    transcript = req.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty.")

    # 1. Layer A: Fast rules/lexicon scorer (always runs, provides explainability)
    rules_res = score_lexicon(transcript)
    rules_score = compute_rules_score(rules_res)
    fired_features = [f["feature"] for f in rules_res.get("fired", [])]
    fired_features_detail = rules_res.get("fired", [])

    # 2. Layer B: Extract 9 engineered features
    eng_feats = extract_features(transcript)

    # 3. Layer C: TF-IDF + LogReg scam probability
    tfidf_prob = tfidf_prob_fn(transcript)

    # 4. Layer D: Fine-tuned Transformer scam probability
    trans_prob = trans_prob_fn(transcript)

    # 5. Layer E: Stacking ensemble meta-classifier
    ensemble_res = score_ensemble(tfidf_prob, trans_prob, rules_score, eng_feats)
    final_score = ensemble_res["score"]
    final_band = ensemble_res["band"]
    stage = ensemble_res["method"] # "ensemble_stacking" or fallback

    # Rules Safety Override: if rules layer fires hard but ensemble is "low", force to needs_review
    # Threshold 0.30 covers single-category credential_harvesting (weight 0.30)
    if rules_score >= 0.30 and final_band == "low":
        final_band = "needs_review"
        stage = "rules_safety_override"

    # Route self-referential queries (asking if something is a scam/safe) to LLM fallback
    text_lower = transcript.lower()
    is_self_referential = "is it a scam" in text_lower or "is it safe" in text_lower or "is this a scam" in text_lower

    llm_res = None
    # 6. Layer F: LLM fallback for borderline / needs_review cases
    if final_band == "needs_review" or is_self_referential:
        llm_res = score_llm(transcript)
        # If the LLM has a clear high/low verdict, we adopt it, otherwise keep needs_review
        if llm_res.get("risk_band") in ["high", "low"]:
            final_band = llm_res["risk_band"]
            final_score = llm_res.get("score", final_score)
            stage = "llm_fallback"
        else:
            final_band = "needs_review"
            stage = llm_res.get("method", "llm_fallback_uncertain")
            final_score = llm_res.get("score", final_score)

    # Assemble response
    component_scores = {
        "rules": float(rules_score),
        "tfidf": float(tfidf_prob),
        "transformer": float(trans_prob),
        "ensemble": float(ensemble_res["score"])
    }
    if llm_res and "score" in llm_res:
        component_scores["llm_fallback"] = float(llm_res["score"])

    breakdown = {
        "engineered_features": eng_feats,
        "rules_detail": fired_features_detail
    }
    if llm_res:
        breakdown["llm_analysis"] = llm_res.get("analysis", "")
        breakdown["llm_reasons"] = llm_res.get("reasons", [])

    return VerdictResponse(
        stage=stage,
        risk_score=round(final_score, 4),
        risk_band=final_band,
        fired_features=fired_features,
        fired_features_detail=fired_features_detail,
        component_scores=component_scores,
        breakdown=breakdown,
        transcript=transcript
    )

@app.post("/api/scam/analyze-audio", response_model=VerdictResponse)
async def analyze_audio(file: UploadFile = File(...)):
    """Transcribes call audio using Whisper and runs the full text classification pipeline."""
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Transcribe audio file to text
        transcript = transcribe_audio(tmp_path)
        if not transcript.strip() or transcript.startswith("[Audio transcription"):
            raise HTTPException(
                status_code=500, 
                detail=f"Audio transcription failed or empty: {transcript}"
            )
            
        # Analyze using text pipeline
        verdict = analyze_text(TextRequest(transcript=transcript))
        verdict.transcript = transcript
        return verdict
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.post("/api/scam/stream")
async def stream_scoring(req: StreamRequest):
    """
    Simulates real-time call interception by streaming risk score updates 
    for every chunk of text added to the conversation.
    """
    async def event_generator():
        running_text = ""
        for chunk in req.transcript_chunks:
            running_text += " " + chunk.strip()
            # Fast lexicon score for streaming updates
            rules_res = score_lexicon(running_text)
            
            payload = {
                "elapsed_chars": len(running_text),
                "risk_score": rules_res["score"],
                "risk_band": rules_res["band"],
                "fired_features": [f["feature"] for f in rules_res.get("fired", [])],
                "fired_details": rules_res.get("fired", [])
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")