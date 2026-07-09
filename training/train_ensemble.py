# training/train_ensemble.py
import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

# Import preprocessing and rules functions
from utils.preprocessing import extract_features, compute_rules_score
from models.rules import score_lexicon

def prepare_features(df, tfidf_probs, transformer_probs):
    """
    Constructs the 12-feature matrix in the exact order expected by the ensemble:
    [
        tfidf_prob, transformer_prob, rules_score, 
        turn_count, char_len, word_count, placeholder_count,
        urgency_word_count, money_word_count, authority_word_count,
        has_phone_number, exclaim_count
    ]
    """
    X = []
    for idx, row in enumerate(df.itertuples()):
        text = str(row.text)
        
        # Calculate rules score
        rules_res = score_lexicon(text)
        rules_score = compute_rules_score(rules_res)
        
        # Extract 9 engineered features
        eng_feats = extract_features(text)
        
        # Build 12-feature vector
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
    
    # 1. Load splits
    val_df = pd.read_csv("data/val.csv").dropna(subset=["text"]).reset_index(drop=True)
    test_df = pd.read_csv("data/test.csv").dropna(subset=["text"]).reset_index(drop=True)
    
    # 2. Load model predictions
    if not os.path.exists("artifacts/metrics/tfidf_val_probs.npy") or not os.path.exists("artifacts/metrics/transformer_val_probs.npy"):
        raise FileNotFoundError("TF-IDF or Transformer validation probabilities are missing. Please run train_tfidf.py and train_transformer.py first.")
        
    tfidf_val_probs = np.load("artifacts/metrics/tfidf_val_probs.npy")
    tfidf_test_probs = np.load("artifacts/metrics/tfidf_test_probs.npy")
    
    trans_val_probs = np.load("artifacts/metrics/transformer_val_probs.npy")
    trans_test_probs = np.load("artifacts/metrics/transformer_test_probs.npy")
    
    # 3. Construct feature matrices
    print("Extracting features for validation set (train data for stacker)...")
    X_val = prepare_features(val_df, tfidf_val_probs, trans_val_probs)
    y_val = val_df["label"].values
    
    print("Extracting features for test set (evaluation data)...")
    X_test = prepare_features(test_df, tfidf_test_probs, trans_test_probs)
    y_test = test_df["label"].values
    
    # 4. Train meta-classifier
    print("Fitting Logistic Regression meta-classifier on validation features...")
    meta_clf = LogisticRegression(class_weight="balanced", random_state=42)
    meta_clf.fit(X_val, y_val)
    
    # Save the meta-model
    os.makedirs("artifacts", exist_ok=True)
    joblib.dump(meta_clf, "artifacts/ensemble_meta.joblib")
    print("Saved ensemble meta-model to artifacts/ensemble_meta.joblib")
    
    # 5. Evaluate on Test set
    y_pred = meta_clf.predict(X_test)
    y_pred_probs = meta_clf.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary")
    acc = accuracy_score(y_test, y_pred)
    
    print("\n--- ENSEMBLE META-CLASSIFIER TEST PERFORMANCE ---")
    print(classification_report(y_test, y_pred, target_names=["Legit", "Scam"]))
    
    print(f"Accuracy : {acc*100:.2f}%")
    print(f"Precision: {precision*100:.2f}%")
    print(f"Recall   : {recall*100:.2f}%")
    print(f"F1-Score : {f1*100:.2f}%")
    
    # Coefficients analysis
    feature_names = [
        "tfidf_prob", "transformer_prob", "rules_score", 
        "turn_count", "char_len", "word_count", "placeholder_count",
        "urgency_word_count", "money_word_count", "authority_word_count",
        "has_phone_number", "exclaim_count"
    ]
    coefs = meta_clf.coef_[0]
    print("\nMeta-Classifier Coefficients:")
    for name, val in zip(feature_names, coefs):
        print(f"  {name:<25}: {val:.4f}")
    print(f"  Intercept                : {meta_clf.intercept_[0]:.4f}")
    
    # Save metrics evaluation
    metrics = {
        "accuracy": float(acc),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "coefficients": {name: float(val) for name, val in zip(feature_names, coefs)},
        "intercept": float(meta_clf.intercept_[0])
    }
    os.makedirs("artifacts/metrics", exist_ok=True)
    with open("artifacts/metrics/ensemble_eval.json", "w") as f:
        json.dump(metrics, f, indent=4)
    print("\nSaved ensemble metrics report to artifacts/metrics/ensemble_eval.json")

if __name__ == "__main__":
    train()
