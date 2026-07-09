# training/calibrate_thresholds.py
import os
import json
import numpy as np
import pandas as pd
import joblib
from utils.preprocessing import extract_features, compute_rules_score
from models.rules import score_lexicon

def get_ensemble_predictions(df, tfidf_probs, transformer_probs, meta_clf):
    """Computes final ensemble scores for each sample."""
    scores = []
    
    for idx, row in enumerate(df.itertuples()):
        text = str(row.text)
        
        # Calculate components
        rules_res = score_lexicon(text)
        rules_score = compute_rules_score(rules_res)
        eng_feats = extract_features(text)
        
        # 12-feature vector
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
        
        # Predict probability of scam (class 1)
        prob = float(meta_clf.predict_proba([feat_vector])[0][1])
        scores.append(prob)
        
    return np.array(scores)

def calibrate():
    print("Calibrating risk thresholds on validation set...")
    
    # 1. Load data and models
    val_df = pd.read_csv("data/val.csv").dropna(subset=["text"]).reset_index(drop=True)
    test_df = pd.read_csv("data/test.csv").dropna(subset=["text"]).reset_index(drop=True)
    
    tfidf_val_probs = np.load("artifacts/metrics/tfidf_val_probs.npy")
    tfidf_test_probs = np.load("artifacts/metrics/tfidf_test_probs.npy")
    
    trans_val_probs = np.load("artifacts/metrics/transformer_val_probs.npy")
    trans_test_probs = np.load("artifacts/metrics/transformer_test_probs.npy")
    
    meta_clf = joblib.load("artifacts/ensemble_meta.joblib")
    
    # 2. Get predictions
    print("Generating validation and test set ensemble scores...")
    val_scores = get_ensemble_predictions(val_df, tfidf_val_probs, trans_val_probs, meta_clf)
    test_scores = get_ensemble_predictions(test_df, tfidf_test_probs, trans_test_probs, meta_clf)
    
    y_val = val_df["label"].values
    y_test = test_df["label"].values
    
    # 3. Sweep thresholds (T_low, T_high)
    print("Sweeping thresholds to meet spec constraints...")
    best_t_low = 0.35
    best_t_high = 0.65
    max_decisive_rate = 0.0
    
    # Grid search for thresholds
    t_low_candidates = np.linspace(0.1, 0.45, 36)
    t_high_candidates = np.linspace(0.55, 0.9, 36)
    
    valid_thresholds = []
    
    for t_low in t_low_candidates:
        for t_high in t_high_candidates:
            # Classify validation set
            preds = [] # high, low, or needs_review
            for score in val_scores:
                if score >= t_high:
                    preds.append("high")
                elif score <= t_low:
                    preds.append("low")
                else:
                    preds.append("needs_review")
                    
            preds = np.array(preds)
            
            # Calculate metrics on decisive calls (binary high/low)
            decisive_mask = (preds != "needs_review")
            decisive_count = np.sum(decisive_mask)
            decisive_rate = decisive_count / len(y_val)
            
            if decisive_count == 0:
                continue
                
            # TP: actual scam, predicted high
            # FP: actual legit, predicted high
            # TN: actual legit, predicted low
            # FN: actual scam, predicted low
            tp = np.sum((y_val == 1) & (preds == "high"))
            fp = np.sum((y_val == 0) & (preds == "high"))
            tn = np.sum((y_val == 0) & (preds == "low"))
            fn = np.sum((y_val == 1) & (preds == "low"))
            
            # Constraints:
            # Binary precision (precision of high calls) >= 90%
            precision_high = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            
            # Overall recall (actual scams caught as high) >= 85%
            total_scams = np.sum(y_val == 1)
            recall_scams = tp / total_scams if total_scams > 0 else 0.0
            
            # False Positive Rate (actual legit predicted high) < 5%
            total_legit = np.sum(y_val == 0)
            fpr = fp / total_legit if total_legit > 0 else 0.0
            
            # Check constraints
            if precision_high >= 0.90 and recall_scams >= 0.85 and fpr < 0.05:
                valid_thresholds.append((t_low, t_high, decisive_rate, precision_high, recall_scams, fpr))
                if decisive_rate > max_decisive_rate:
                    max_decisive_rate = decisive_rate
                    best_t_low = float(t_low)
                    best_t_high = float(t_high)
                    
    # If no configuration strictly satisfies all constraints, select best effort
    if not valid_thresholds:
        print("Warning: No thresholds satisfied all constraints strictly. Using default/best-effort thresholds.")
        # Fallback search maximizing decisive rate with looser constraints
        for t_low in t_low_candidates:
            for t_high in t_high_candidates:
                tp = np.sum((y_val == 1) & (val_scores >= t_high))
                fp = np.sum((y_val == 0) & (val_scores >= t_high))
                tn = np.sum((y_val == 0) & (val_scores <= t_low))
                fn = np.sum((y_val == 1) & (val_scores <= t_low))
                
                precision_high = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                total_scams = np.sum(y_val == 1)
                recall_scams = tp / total_scams if total_scams > 0 else 0.0
                
                # Loose check
                if precision_high >= 0.85 and recall_scams >= 0.80:
                    decisive_rate = np.sum((val_scores >= t_high) | (val_scores <= t_low)) / len(y_val)
                    if decisive_rate > max_decisive_rate:
                        max_decisive_rate = decisive_rate
                        best_t_low = float(t_low)
                        best_t_high = float(t_high)
                        
    print(f"Selected Calibrated Thresholds: Low={best_t_low:.4f}, High={best_t_high:.4f}")
    print(f"Validation Decisive Rate: {max_decisive_rate*100:.2f}%")
    
    # Save calibrated thresholds
    thresholds_data = {
        "low": best_t_low,
        "high": best_t_high,
        "needs_review_low": best_t_low,
        "needs_review_high": best_t_high
    }
    with open("artifacts/calibrated_thresholds.json", "w") as f:
        json.dump(thresholds_data, f, indent=4)
    print("Saved thresholds to artifacts/calibrated_thresholds.json")
    
    # 4. Evaluate on held-out test.csv
    test_preds = []
    for score in test_scores:
        if score >= best_t_high:
            test_preds.append("high")
        elif score <= best_t_low:
            test_preds.append("low")
        else:
            test_preds.append("needs_review")
            
    test_preds = np.array(test_preds)
    
    tp_t = np.sum((y_test == 1) & (test_preds == "high"))
    fp_t = np.sum((y_test == 0) & (test_preds == "high"))
    tn_t = np.sum((y_test == 0) & (test_preds == "low"))
    fn_t = np.sum((y_test == 1) & (test_preds == "low"))
    nr_t = np.sum(test_preds == "needs_review")
    
    test_precision = tp_t / (tp_t + fp_t) if (tp_t + fp_t) > 0 else 0.0
    test_recall = tp_t / np.sum(y_test == 1) if np.sum(y_test == 1) > 0 else 0.0
    test_fpr = fp_t / np.sum(y_test == 0) if np.sum(y_test == 0) > 0 else 0.0
    test_accuracy = (tp_t + tn_t) / (len(y_test) - nr_t) if (len(y_test) - nr_t) > 0 else 0.0
    
    print("\nHeld-out Test Set Calibrated Metrics:")
    print(f"Precision:         {test_precision*100:.2f}%")
    print(f"Recall:            {test_recall*100:.2f}%")
    print(f"False Positive Rate: {test_fpr*100:.2f}%")
    print(f"Needs Review Rate:  {nr_t / len(y_test)*100:.2f}%")
    print(f"Decisive Accuracy:  {test_accuracy*100:.2f}%")
    
    # 5. Write final_eval.json matching requirements
    final_report = {
        "thresholds": thresholds_data,
        "test_metrics": {
            "precision": float(test_precision),
            "recall": float(test_recall),
            "fpr": float(test_fpr),
            "accuracy_decisive": float(test_accuracy),
            "needs_review_count": int(nr_t),
            "needs_review_rate": float(nr_t / len(y_test))
        },
        "confusion_matrix": {
            "tp": int(tp_t),
            "fp": int(fp_t),
            "tn": int(tn_t),
            "fn": int(fn_t)
        },
        "comparison_to_baselines": {
            "ieee_lstm_baseline_accuracy": 0.8561,
            "our_decisive_accuracy": float(test_accuracy),
            "improvement_pct": float(test_accuracy - 0.8561)
        }
    }
    
    with open("artifacts/metrics/final_eval.json", "w") as f:
        json.dump(final_report, f, indent=4)
    print("Saved final evaluation report to artifacts/metrics/final_eval.json")

if __name__ == "__main__":
    calibrate()
