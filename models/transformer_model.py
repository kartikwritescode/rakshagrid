# models/transformer_model.py
from transformers import pipeline

_classifier = pipeline(
    "text-classification",
    model="artifacts/scam-distilbert",
    tokenizer="artifacts/scam-distilbert",
    top_k=None,
)

def score_transformer(transcript: str) -> dict:
    results = _classifier(transcript)[0]     # [{'label': 'LABEL_0', 'score': ...}, {'label': 'LABEL_1', 'score': ...}]
    scam_prob = next(r["score"] for r in results if r["label"] == "LABEL_1")
    band = "high" if scam_prob > 0.6 else "medium" if scam_prob > 0.3 else "low"
    return {"score": float(scam_prob), "band": band}