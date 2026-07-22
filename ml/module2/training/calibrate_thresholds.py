# ml/module2/training/calibrate_thresholds.py
import os
import json
import numpy as np
import pandas as pd
import joblib
from ml.module2.preprocessing.text_processor import extract_features, compute_rules_score
from ml.module2.model.rules import score_lexicon

def get_ensemble_predictions(df, tfidf_probs, transformer_probs, meta_clf):
    scores = []
    for idx, row in enumerate(df.itertuples()):
        text = str(row.text)
        rules_res = score_lexicon(text)
        rules_score = compute_rules_score(rules_res)
        eng_feats = extract_features(text)
        
        feat_vector = [
            float(tfidf_probs[idx]),
            float(transformer_probs[idx]),
            float(rules_score),
            float(eng_feats["turn_count"]),
            float(eng_feats["char_len"]),
            float(eng_feats["word_count"]),
            float(eng_feats["placeholder_count"]),
            float(eng_feats["urgency_word_count"]),
            float(eng_feats["money_word_count"]),
            float(eng_feats["authority_word_count"]),
            float(eng_feats["has_phone_number"]),
            float(eng_feats["exclaim_count"])
        ]
        prob = float(meta_clf.predict_proba([feat_vector])[0][1])
        scores.append(prob)
    return np.array(scores)

def calibrate():
    print("Calibrating risk thresholds on validation set...")
    val_df = pd.read_csv("data/val.csv").dropna(subset=["text"]).reset_index(drop=True)
    test_df = pd.read_csv("data/test.csv").dropna(subset=["text"]).reset_index(drop=True)
    
    tfidf_val_probs = np.load("artifacts/metrics/tfidf_val_probs.npy")
    tfidf_test_probs = np.load("artifacts/metrics/tfidf_test_probs.npy")
    trans_val_probs = np.load("artifacts/metrics/transformer_val_probs.npy")
    trans_test_probs = np.load("artifacts/metrics/transformer_test_probs.npy")
    
    meta_clf = joblib.load("artifacts/ensemble_meta.joblib")
    
    val_scores = get_ensemble_predictions(val_df, tfidf_val_probs, trans_val_probs, meta_clf)
    test_scores = get_ensemble_predictions(test_df, tfidf_test_probs, trans_test_probs, meta_clf)
    
    y_val = val_df["label"].values
    y_test = test_df["label"].values
    
    best_t_low = 0.12
    best_t_high = 0.55
    max_decisive_rate = 0.0
    
    t_low_candidates = np.linspace(0.1, 0.45, 36)
    t_high_candidates = np.linspace(0.55, 0.9, 36)
    valid_thresholds = []
    
    for t_low in t_low_candidates:
        for t_high in t_high_candidates:
            if (t_high - t_low) < 0.35:
                continue
            preds = []
            for score in val_scores:
                if score >= t_high:
                    preds.append("high")
                elif score <= t_low:
                    preds.append("low")
                else:
                    preds.append("needs_review")
            preds = np.array(preds)
            
            decisive_mask = (preds != "needs_review")
            decisive_count = np.sum(decisive_mask)
            decisive_rate = decisive_count / len(y_val)
            if decisive_count == 0:
                continue
                
            tp = np.sum((y_val == 1) & (preds == "high"))
            fp = np.sum((y_val == 0) & (preds == "high"))
            
            precision_high = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            total_scams = np.sum(y_val == 1)
            recall_scams = tp / total_scams if total_scams > 0 else 0.0
            total_legit = np.sum(y_val == 0)
            fpr = fp / total_legit if total_legit > 0 else 0.0
            
            if precision_high >= 0.90 and recall_scams >= 0.85 and fpr < 0.05:
                valid_thresholds.append((t_low, t_high, decisive_rate, precision_high, recall_scams, fpr))
                if decisive_rate > max_decisive_rate:
                    max_decisive_rate = decisive_rate
                    best_t_low = float(t_low)
                    best_t_high = float(t_high)
                    
    thresholds_data = {
        "low": best_t_low,
        "high": best_t_high,
        "needs_review_low": best_t_low,
        "needs_review_high": best_t_high
    }
    
    os.makedirs("storage/models", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)
    with open("storage/models/calibrated_thresholds.json", "w") as f:
        json.dump(thresholds_data, f, indent=4)
    with open("artifacts/calibrated_thresholds.json", "w") as f:
        json.dump(thresholds_data, f, indent=4)
        
    print(f"Calibrated Thresholds: Low={best_t_low:.4f}, High={best_t_high:.4f}")

if __name__ == "__main__":
    calibrate()
