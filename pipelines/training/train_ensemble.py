# ml/module2/training/train_ensemble.py
import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

from rakshagrid.ai_scam.preprocessing.text_processor import extract_features, compute_rules_score
from rakshagrid.ai_scam.model.rules import score_lexicon
from rakshagrid.ai_scam.model.ensemble import BoundedLogisticRegression

FEATURE_NAMES = [
    "tfidf_prob", "transformer_prob", "rules_score", 
    "turn_count", "char_len", "word_count", "placeholder_count",
    "urgency_word_count", "money_word_count", "authority_word_count",
    "has_phone_number", "exclaim_count"
]

NON_NEGATIVE_INDICES = [0, 1, 2]

def prepare_features(df, tfidf_probs, transformer_probs):
    X = []
    for idx, row in enumerate(df.itertuples()):
        text = str(row.text)
        rules_res = score_lexicon(text)
        rules_score = compute_rules_score(rules_res)
        eng_feats = extract_features(text)
        
        feature_vector = [
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
        X.append(feature_vector)
    return np.array(X)

def train():
    print("=== TRAINING ENSEMBLE META-CLASSIFIER ===")
    val_df = pd.read_csv("data/val.csv").dropna(subset=["text"]).reset_index(drop=True)
    test_df = pd.read_csv("data/test.csv").dropna(subset=["text"]).reset_index(drop=True)
    
    tfidf_val_probs = np.load("artifacts/metrics/tfidf_val_probs.npy")
    tfidf_test_probs = np.load("artifacts/metrics/tfidf_test_probs.npy")
    trans_val_probs = np.load("artifacts/metrics/transformer_val_probs.npy")
    trans_test_probs = np.load("artifacts/metrics/transformer_test_probs.npy")
    
    X_val = prepare_features(val_df, tfidf_val_probs, trans_val_probs)
    y_val = val_df["label"].values
    X_test = prepare_features(test_df, tfidf_test_probs, trans_test_probs)
    y_test = test_df["label"].values
    
    meta_clf = BoundedLogisticRegression(
        non_negative_indices=NON_NEGATIVE_INDICES,
        C=1.0,
        random_state=42
    )
    meta_clf.fit(X_val, y_val)
    
    os.makedirs("storage/models", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)
    joblib.dump(meta_clf, "storage/models/ensemble_meta.joblib")
    joblib.dump(meta_clf, "artifacts/ensemble_meta.joblib")
    
    y_pred = meta_clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary")
    
    print("\n--- ENSEMBLE META-CLASSIFIER TEST PERFORMANCE ---")
    print(classification_report(y_test, y_pred, target_names=["Legit", "Scam"]))
    
    coefs = meta_clf.coef_[0]
    metrics = {
        "accuracy": float(acc),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "coefficients": {name: float(val) for name, val in zip(FEATURE_NAMES, coefs)},
        "intercept": float(meta_clf.intercept_[0])
    }
    os.makedirs("artifacts/metrics", exist_ok=True)
    with open("artifacts/metrics/ensemble_eval.json", "w") as f:
        json.dump(metrics, f, indent=4)

if __name__ == "__main__":
    train()

