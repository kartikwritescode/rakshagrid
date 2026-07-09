# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import TextRequest, VerdictResponse
from models.rules import score_lexicon

from models.rules import score_lexicon
from models.tfidf_model import score_tfidf
from models.transformer_model import score_transformer
from models.llm_fallback import score_llm


# main.py (add this route)
from fastapi.responses import StreamingResponse
import asyncio, json


# main.py (add this route)
from fastapi import UploadFile, File
import shutil, tempfile
from models.audio import transcribe_audio


app = FastAPI(title="Scam Detection Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # lock this down to your Next.js domain later
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/scam/analyze-text", response_model=VerdictResponse)
def analyze_text(req: TextRequest):
    result = score_lexicon(req.transcript)
    return VerdictResponse(
        stage="rules",
        risk_score=result["score"],
        risk_band=result["band"],
        fired_features=[f["feature"] for f in result["fired"]],
        breakdown={"rules_detail": result["fired"]},
    )

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/scam/analyze-text", response_model=VerdictResponse)
def analyze_text(req: TextRequest):
    rules = score_lexicon(req.transcript)
    transformer = score_transformer(req.transcript)

    stage = "transformer"
    final_score = transformer["score"]
    final_band = transformer["band"]

    # borderline zone -> ask the LLM for a second opinion
    if 0.35 < transformer["score"] < 0.65:
        llm = score_llm(req.transcript)
        stage = "llm_fallback"
        final_score = llm["confidence"]
        final_band = "high" if llm["is_scam"] else "low"

    return VerdictResponse(
        stage=stage,
        risk_score=round(final_score, 3),
        risk_band=final_band,
        fired_features=[f["feature"] for f in rules["fired"]],   # explainability always from rules layer
        breakdown={
            "rules_score": rules["score"],
            "transformer_score": transformer["score"],
        },
    )



class StreamRequest(BaseModel):
    transcript_chunks: List[str]

@app.post("/api/scam/stream")
async def stream_scoring(req: StreamRequest):
    async def event_generator():
        running_text = ""
        for chunk in req.transcript_chunks:
            running_text += " " + chunk
            result = score_lexicon(running_text)   # fast layer for every chunk
            payload = {
                "elapsed_chars": len(running_text),
                "risk_score": result["score"],
                "risk_band": result["band"],
                "fired_features": [f["feature"] for f in result["fired"]],
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")



@app.post("/api/scam/analyze-audio", response_model=VerdictResponse)
async def analyze_audio(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    transcript = transcribe_audio(tmp_path)
    return analyze_text(TextRequest(transcript=transcript))