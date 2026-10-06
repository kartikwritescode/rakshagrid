# ml/module2/training/eval_adversarial.py
import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

from rakshagrid.ai_scam.preprocessing.text_processor import extract_features, compute_rules_score
from rakshagrid.ai_scam.utils.helpers import get_risk_band, get_calibrated_thresholds
from rakshagrid.ai_scam.model.rules import score_lexicon
from rakshagrid.ai_scam.model.tfidf import get_scam_probability as tfidf_prob_fn
from rakshagrid.ai_scam.model.transformer import get_scam_probability as trans_prob_fn
from rakshagrid.ai_scam.model.ensemble import score_ensemble
from rakshagrid.ai_scam.model.llm_fallback import score_llm

def run_adversarial_eval():
    print("=== STARTING ADVERSARIAL EVALUATION ===")
    if not os.path.exists("data/adversarial_eval.csv"):
        print("data/adversarial_eval.csv not found.")
        return
        
    df = pd.read_csv("data/adversarial_eval.csv")
    thresholds = get_calibrated_thresholds()
    
    results = []
    for idx, row in enumerate(df.itertuples()):
        text = str(row.text)
        true_label = int(row.label)
        category = str(row.category)
        
        rules_res = score_lexicon(text)
        rules_score = compute_rules_score(rules_res)
        eng_feats = extract_features(text)
        tfidf_prob = tfidf_prob_fn(text)
        trans_prob = trans_prob_fn(text)
        
        ensemble_res = score_ensemble(tfidf_prob, trans_prob, rules_score, eng_feats)
        final_score = ensemble_res["score"]
        final_band = ensemble_res["band"]
        stage = ensemble_res["method"]
        
        if rules_score >= 0.30 and final_band == "low":
            final_band = "needs_review"
            stage = "rules_safety_override"
            
        text_lower = text.lower()
        is_self_referential = "is it a scam" in text_lower or "is it safe" in text_lower or "is this a scam" in text_lower
        
        llm_res = None
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

        results.append({
            "text": text,
            "true_label": true_label,
            "category": category,
            "score": final_score,
            "band": final_band,
            "stage": stage
        })
        
    print(f"Evaluated {len(results)} adversarial examples.")

if __name__ == "__main__":
    run_adversarial_eval()

