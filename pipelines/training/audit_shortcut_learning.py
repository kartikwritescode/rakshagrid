# training/audit_shortcut_learning.py
import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

def audit():
    print("=== STARTING SHORTCUT LEARNING AND DATA INTEGRITY AUDIT ===")
    
    # Load splits
    train_df = pd.read_csv("data/train.csv").dropna(subset=["text"]).reset_index(drop=True)
    test_df = pd.read_csv("data/test.csv").dropna(subset=["text"]).reset_index(drop=True)
    
    # Load TF-IDF artifacts
    vectorizer = joblib.load("artifacts/tfidf_vectorizer.joblib")
    clf = joblib.load("artifacts/tfidf_logreg.joblib")
    
    # 1. TF-IDF Coefficients Audit
    feature_names = vectorizer.get_feature_names_out()
    coef = clf.coef_[0]
    
    # Sort features by coefficient value
    sorted_indices = np.argsort(coef)
    
    # Top 30 negative coefficients (Legit-indicative)
    top_legit = [(feature_names[idx], coef[idx]) for idx in sorted_indices[:30]]
    # Top 30 positive coefficients (Scam-indicative)
    top_scam = [(feature_names[idx], coef[idx]) for idx in sorted_indices[::-1][:30]]
    
    print("\n--- TOP 30 LEGIT-INDICATIVE TF-IDF FEATURES (Negative Coefs) ---")
    for feat, score in top_legit:
        print(f"  {feat:<25}: {score:.4f}")
        
    print("\n--- TOP 30 SCAM-INDICATIVE TF-IDF FEATURES (Positive Coefs) ---")
    for feat, score in top_scam:
        print(f"  {feat:<25}: {score:.4f}")
        
    # 2. Near-Duplicate Leakage Check (Train vs Test)
    print("\nChecking train-test near-duplicate leakage using TF-IDF cosine similarity...")
    X_train_vec = vectorizer.transform(train_df["text"])
    X_test_vec = vectorizer.transform(test_df["text"])
    
    # Compute cosine similarity matrix (shape: num_test, num_train)
    # Since vectors are normalized, dot product is cosine similarity
    from sklearn.metrics.pairwise import cosine_similarity
    sim_matrix = cosine_similarity(X_test_vec, X_train_vec)
    
    leakage_count = 0
    leaked_indices = []
    
    for test_idx in range(sim_matrix.shape[0]):
        max_sim = np.max(sim_matrix[test_idx])
        if max_sim >= 0.9:
            leakage_count += 1
            train_idx = np.argmax(sim_matrix[test_idx])
            leaked_indices.append((test_idx, train_idx, max_sim))
            
    leakage_pct = (leakage_count / len(test_df)) * 100
    print(f"Total test examples with >= 0.9 similarity to a training example: {leakage_count} / {len(test_df)} ({leakage_pct:.2f}%)")
    
    if leakage_count > 0:
        print("\nExamples of leaked / near-duplicate pairs:")
        for test_i, train_i, sim in leaked_indices[:3]:
            print(f"\nSimilarity: {sim:.4f}")
            print(f"TEST (Label {test_df.iloc[test_i]['label']}): {test_df.iloc[test_i]['text'][:120]}...")
            print(f"TRAIN (Label {train_df.iloc[train_i]['label']}): {train_df.iloc[train_i]['text'][:120]}...")
            
    # 3. Performance Breakdown by Source Column
    print("\n--- TF-IDF PERFORMANCE BREAKDOWN BY DATA SOURCE ---")
    # Generate predictions
    y_test_pred = clf.predict(X_test_vec)
    test_df["pred"] = y_test_pred
    
    sources = test_df["source"].unique()
    for src in sources:
        src_df = test_df[test_df["source"] == src]
        if len(src_df) == 0:
            continue
        y_src_true = src_df["label"].values
        y_src_pred = src_df["pred"].values
        
        # Calculate metrics
        acc = accuracy_score(y_src_true, y_src_pred)
        # Handle zero-division warnings safely
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_src_true, y_src_pred, average="binary", zero_division=0
        )
        
        print(f"\nSource: {src} (Sample size: {len(src_df)})")
        print(f"  Accuracy : {acc*100:.2f}%")
        print(f"  Precision: {precision*100:.2f}%")
        print(f"  Recall   : {recall*100:.2f}%")
        print(f"  F1-Score : {f1*100:.2f}%")

if __name__ == "__main__":
    audit()

