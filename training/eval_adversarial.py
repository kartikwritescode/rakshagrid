# training/eval_adversarial.py
import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix

# Import components from the pipeline
from utils.preprocessing import extract_features, compute_rules_score
from utils.helpers import get_risk_band, get_calibrated_thresholds
from models.rules import score_lexicon
from models.tfidf_model import get_scam_probability as tfidf_prob_fn
from models.transformer_model import get_scam_probability as trans_prob_fn
from models.ensemble import score_ensemble
from models.llm_fallback import score_llm

def run_adversarial_eval():
    print("=== STARTING ADVERSARIAL EVALUATION ===")
    
    # 1. Load adversarial eval set
    if not os.path.exists("data/adversarial_eval.csv"):
        raise FileNotFoundError("Adversarial evaluation set data/adversarial_eval.csv not found.")
        
    df = pd.read_csv("data/adversarial_eval.csv")
    print(f"Loaded {len(df)} hand-written adversarial examples.")
    
    results = []
    
    thresholds = get_calibrated_thresholds()
    print(f"Active Thresholds: Low={thresholds['low']:.4f}, High={thresholds['high']:.4f}")
    
    for idx, row in enumerate(df.itertuples()):
        text = str(row.text)
        true_label = int(row.label)
        category = str(row.category)
        
        # 1. Rules Layer
        rules_res = score_lexicon(text)
        rules_score = compute_rules_score(rules_res)
        
        # 2. Engineered Features
        eng_feats = extract_features(text)
        
        # 3. TF-IDF
        tfidf_prob = tfidf_prob_fn(text)
        
        # 4. Transformer
        trans_prob = trans_prob_fn(text)
        
        # 5. Stacking Ensemble
        ensemble_res = score_ensemble(tfidf_prob, trans_prob, rules_score, eng_feats)
        ensemble_score = ensemble_res["score"]
        ensemble_band = ensemble_res["band"]
        
        # Initialize final variables
        final_score = ensemble_score
        final_band = ensemble_band
        stage = ensemble_res["method"]
        
        # 6. LLM Fallback (if final_band is needs_review)
        llm_triggered = False
        if final_band == "needs_review":
            llm_triggered = True
            llm_res = score_llm(text)
            if llm_res.get("risk_band") in ["high", "low"]:
                final_band = llm_res["risk_band"]
                final_score = llm_res.get("score", final_score)
                stage = "llm_fallback"
            else:
                final_band = "needs_review"
                stage = "llm_fallback_uncertain"
                
        # Map final band to a binary predicted label:
        # High -> 1
        # Low -> 0
        # Needs Review -> -1 (uncertain)
        if final_band == "high":
            pred_label = 1
        elif final_band == "low":
            pred_label = 0
        else:
            pred_label = -1 # Needs review
            
        results.append({
            "text": text,
            "true_label": true_label,
            "category": category,
            "rules_score": rules_score,
            "tfidf_prob": tfidf_prob,
            "trans_prob": trans_prob,
            "ensemble_score": ensemble_score,
            "ensemble_band": ensemble_band,
            "final_score": final_score,
            "final_band": final_band,
            "stage": stage,
            "pred_label": pred_label,
            "llm_triggered": llm_triggered,
            "format": str(row.format)
        })
        
    results_df = pd.DataFrame(results)
    
    # 2. Analyze Decisive vs Needs Review rates
    total = len(results_df)
    ensemble_review_count = sum(results_df["ensemble_band"] == "needs_review")
    ensemble_review_pct = (ensemble_review_count / total) * 100
    
    needs_review_count = sum(results_df["final_band"] == "needs_review")
    needs_review_pct = (needs_review_count / total) * 100
    
    decisive_df = results_df[results_df["final_band"] != "needs_review"]
    decisive_count = len(decisive_df)
    decisive_pct = (decisive_count / total) * 100
    
    print(f"\n--- BAND DISTRIBUTION ---")
    print(f"  Low Risk                 : {sum(results_df['final_band'] == 'low')} / {total}")
    print(f"  High Risk                : {sum(results_df['final_band'] == 'high')} / {total}")
    print(f"  Ensemble Borderline Rate : {ensemble_review_count} / {total} ({ensemble_review_pct:.2f}%)")
    print(f"  Final Needs Review Rate  : {needs_review_count} / {total} ({needs_review_pct:.2f}%)")
    
    # 3. Calculate metrics on decisive cases
    print(f"\n--- DECISIVE PERFORMANCE (Excluding Needs Review) ---")
    if decisive_count > 0:
        y_true_decisive = decisive_df["true_label"].values
        y_pred_decisive = decisive_df["pred_label"].values
        
        acc = accuracy_score(y_true_decisive, y_pred_decisive)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true_decisive, y_pred_decisive, average="binary", zero_division=0
        )
        
        # Calculate FPR
        tn, fp, fn, tp = confusion_matrix(y_true_decisive, y_pred_decisive, labels=[0, 1]).ravel()
        fpr = fp / (tn + fp) if (tn + fp) > 0 else 0.0
        
        print(classification_report(y_true_decisive, y_pred_decisive, target_names=["Legit", "Scam"], zero_division=0))
        print(f"Decisive Accuracy: {acc*100:.2f}%")
        print(f"Precision:         {precision*100:.2f}%")
        print(f"Recall:            {recall*100:.2f}%")
        print(f"F1-Score:          {f1*100:.2f}%")
        print(f"False Positive Rate: {fpr*100:.2f}%")
    else:
        print("No decisive cases. All cases fell to Needs Review.")
        precision, recall, f1, acc, fpr = 0.0, 0.0, 0.0, 0.0, 0.0
        
    # 4. Calculate overall performance (treating Needs Review as incorrect or using standard classification)
    # Let's map pred_label == -1 (needs_review) to a default class or evaluate standard accuracy where needs_review is a mistake
    print(f"\n--- OVERALL SYSTEM PERFORMANCE (All Cases, Needs Review treated as Incorrect/Mismatched) ---")
    # For a strict evaluation, any needs_review case is not decisive, so we see what the classification is if we map needs_review to the opposite of true
    y_true_all = results_df["true_label"].values
    y_pred_all = []
    for r in results:
        if r["final_band"] == "high":
            y_pred_all.append(1)
        elif r["final_band"] == "low":
            y_pred_all.append(0)
        else:
            # Map to wrong answer so it penalizes the accuracy/F1
            y_pred_all.append(1 - r["true_label"])
            
    overall_acc = accuracy_score(y_true_all, y_pred_all)
    overall_p, overall_r, overall_f1, _ = precision_recall_fscore_support(y_true_all, y_pred_all, average="binary", zero_division=0)
    print(f"Strict System Accuracy : {overall_acc*100:.2f}%")
    print(f"Strict System F1-Score : {overall_f1*100:.2f}%")
    
    # 5. Print misclassified or needs_review examples
    print("\n--- MISCLASSIFIED AND BORDERLINE/NEEDS_REVIEW EXAMPLES ---")
    misclassified_count = 0
    for r in results:
        is_error = (r["pred_label"] != -1 and r["pred_label"] != r["true_label"])
        is_review = (r["pred_label"] == -1)
        
        if is_error or is_review:
            misclassified_count += 1
            status = "MISCLASSIFIED" if is_error else "NEEDS_REVIEW"
            print(f"\n[{status}] True Label: {r['true_label']} | Category: {r['category']}")
            print(f"  Text: {repr(r['text'])}")
            print(f"  Scores: Rules={r['rules_score']:.4f} | TF-IDF={r['tfidf_prob']:.4f} | Trans={r['trans_prob']:.4f} | Ensemble={r['ensemble_score']:.4f}")
            print(f"  Verdict: Band={r['final_band']} | Score={r['final_score']:.4f} | Stage={r['stage']} | LLM Triggered={r['llm_triggered']}")
            
    print(f"\nTotal misclassified or reviewed examples: {misclassified_count} / {total}")
    
    # 6. Format-specific metrics check
    print("\n--- FORMAT ROBUSTNESS COMPARISON ---")
    format_metrics = {}
    for fmt in results_df["format"].unique():
        fmt_df = results_df[results_df["format"] == fmt]
        fmt_decisive = fmt_df[fmt_df["final_band"] != "needs_review"]
        
        if len(fmt_decisive) > 0:
            y_t_fmt = fmt_decisive["true_label"].values
            y_p_fmt = fmt_decisive["pred_label"].values
            
            acc_fmt = accuracy_score(y_t_fmt, y_p_fmt)
            p_fmt, r_fmt, f1_fmt, _ = precision_recall_fscore_support(y_t_fmt, y_p_fmt, average="binary", zero_division=0)
            tn_fmt, fp_fmt, fn_fmt, tp_fmt = confusion_matrix(y_t_fmt, y_p_fmt, labels=[0, 1]).ravel()
            fpr_fmt = fp_fmt / (tn_fmt + fp_fmt) if (tn_fmt + fp_fmt) > 0 else 0.0
            
            print(f"Format: {fmt:<8} (Decisive count: {len(fmt_decisive)} / {len(fmt_df)})")
            print(f"  Accuracy : {acc_fmt*100:.2f}%")
            print(f"  Precision: {p_fmt*100:.2f}%")
            print(f"  Recall   : {r_fmt*100:.2f}%")
            print(f"  FPR      : {fpr_fmt*100:.2f}%")
            
            format_metrics[fmt] = {
                "accuracy": float(acc_fmt),
                "precision": float(p_fmt),
                "recall": float(r_fmt),
                "f1": float(f1_fmt),
                "fpr": float(fpr_fmt),
                "decisive_count": int(len(fmt_decisive))
            }
        else:
            print(f"Format: {fmt} - No decisive cases.")

    # Save adversarial evaluation results
    adversarial_report = {
        "dataset_size": total,
        "needs_review_pct": needs_review_pct,
        "decisive_pct": decisive_pct,
        "decisive_metrics": {
            "accuracy": float(acc),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "fpr": float(fpr)
        },
        "overall_strict_metrics": {
            "accuracy": float(overall_acc),
            "precision": float(overall_p),
            "recall": float(overall_r),
            "f1": float(overall_f1)
        },
        "format_metrics": format_metrics
    }
    
    os.makedirs("artifacts/metrics", exist_ok=True)
    with open("artifacts/metrics/adversarial_eval.json", "w") as f:
        json.dump(adversarial_report, f, indent=4)
    print("\nSaved adversarial evaluation report to artifacts/metrics/adversarial_eval.json")

if __name__ == "__main__":
    run_adversarial_eval()
