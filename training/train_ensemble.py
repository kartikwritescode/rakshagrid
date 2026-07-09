# training/train_ensemble.py
import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from utils.preprocessing import extract_features, compute_rules_score
from models.rules import score_lexicon

def prepare_feature_matrix(df, tfidf_probs, transformer_probs):
    """
    Constructs a 12-feature matrix for stacking:
    [tfidf_prob, transformer_prob, rules_score, 9 engineered features]
    """
    X = []
    y = df["label"].values
    
    for idx, row in enumerate(df.itertuples()):
        text = str(row.text)
        
        # Calculate rules score
        rules_res = score_lexicon(text)
        rules_score = compute_rules_score(rules_res)
        
        # Extract 9 engineered features
        eng_feats = extract_features(text)
        
        # Gather all features in the exact specified order
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
        X.append(feat_vector)
        
    return np.array(X), y

def train():
    print("Training Stacking Ensemble Meta-Classifier...")
    
    # 1. Load splits and probabilities
    val_df = pd.read_csv("data/val.csv").dropna(subset=["text"]).reset_index(drop=True)
    test_df = pd.read_csv("data/test.csv").dropna(subset=["text"]).reset_index(drop=True)
    
    tfidf_val_probs = np.load("artifacts/metrics/tfidf_val_probs.npy")
    tfidf_test_probs = np.load("artifacts/metrics/tfidf_test_probs.npy")
    
    trans_val_probs = np.load("artifacts/metrics/transformer_val_probs.npy")
    trans_test_probs = np.load("artifacts/metrics/transformer_test_probs.npy")
    
    # 2. Build feature matrices
    print("Assembling feature matrices for stacking...")
    X_val, y_val = prepare_feature_matrix(val_df, tfidf_val_probs, trans_val_probs)
    X_test, y_test = prepare_feature_matrix(test_df, tfidf_test_probs, trans_test_probs)
    
    # 3. Train meta-classifier
    # Use LogisticRegression to prevent overfitting on the small validation dataset
    print("Training LogisticRegression meta-model...")
    meta_clf = LogisticRegression(random_state=42)
    meta_clf.fit(X_val, y_val)
    
    # Save the meta-model
    joblib.dump(meta_clf, "artifacts/ensemble_meta.joblib")
    print("Saved ensemble meta-model to artifacts/ensemble_meta.joblib")
    
    # 4. Evaluate meta-classifier on test set
    y_pred = meta_clf.predict(X_test)
    y_pred_probs = meta_clf.predict_proba(X_test)[:, 1]
    
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary")
    ensemble_metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1)
    }
    
    print("\nEnsemble Test Set Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Compare with TF-IDF and Transformer solo models
    with open("artifacts/metrics/tfidf_eval.json", "r") as f:
        tfidf_metrics = json.load(f)
    with open("artifacts/metrics/transformer_eval.json", "r") as f:
        trans_metrics = json.load(f)
        
    print("\nPerformance Comparison:")
    print(f"TF-IDF Solo F1:       {tfidf_metrics['f1']:.4f}")
    print(f"Transformer Solo F1:  {trans_metrics['test_f1']:.4f}")
    print(f"Ensemble Stacked F1:  {ensemble_metrics['f1']:.4f}")
    
    # Save comparison report
    comparison_report = {
        "tfidf_metrics": tfidf_metrics,
        "transformer_metrics": trans_metrics,
        "ensemble_metrics": ensemble_metrics,
        "beats_both": bool(ensemble_metrics["f1"] >= tfidf_metrics["f1"] and ensemble_metrics["f1"] >= trans_metrics["test_f1"])
    }
    
    with open("artifacts/metrics/ensemble_eval.json", "w") as f:
        json.dump(comparison_report, f, indent=4)
        
    print("Saved metrics comparison report.")

if __name__ == "__main__":
    train()
