# ml/module2/training/train_tfidf.py
import os
import pandas as pd
import numpy as np
import joblib
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

def train():
    print("Starting TF-IDF Model Training...")
    
    # 1. Load pre-split datasets
    train_df = pd.read_csv("data/train.csv")
    val_df = pd.read_csv("data/val.csv")
    test_df = pd.read_csv("data/test.csv")
    
    train_df = train_df.dropna(subset=["text"])
    val_df = val_df.dropna(subset=["text"])
    test_df = test_df.dropna(subset=["text"])
    
    X_train, y_train = train_df["text"], train_df["label"]
    X_val, y_val = val_df["text"], val_df["label"]
    X_test, y_test = test_df["text"], test_df["label"]
    
    # 2. Vectorize text with custom stop words
    from sklearn.feature_extraction import text
    conversational_fillers = {
        "hello", "hi", "hey", "greetings", "caller", "receiver", "yes", "okay", "ok", "uh", "um", 
        "ah", "yeah", "john", "david", "alex", "acme", "corp", "company", "xyz", "abc", "mr", "mrs", 
        "thanks", "thank", "good", "morning", "afternoon", "evening", "expecting", "expect", "expecting today",
        "stargazing", "telescopes", "cocoa", "guidance",
        "microsoft", "amazon", "netflix", "walmart"
    }
    stop_words = list(text.ENGLISH_STOP_WORDS.union(conversational_fillers))
    
    vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), stop_words=stop_words)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)
    X_test_vec = vectorizer.transform(X_test)
    
    # 3. Fit classifier
    clf = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    clf.fit(X_train_vec, y_train)
    
    # 4. Save model and vectorizer
    os.makedirs("storage/models", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)
    joblib.dump(vectorizer, "storage/models/tfidf_vectorizer.joblib")
    joblib.dump(clf, "storage/models/tfidf_logreg.joblib")
    joblib.dump(vectorizer, "artifacts/tfidf_vectorizer.joblib")
    joblib.dump(clf, "artifacts/tfidf_logreg.joblib")
    
    # 5. Extract probabilities
    val_probs = clf.predict_proba(X_val_vec)[:, 1]
    test_probs = clf.predict_proba(X_test_vec)[:, 1]
    
    os.makedirs("artifacts/metrics", exist_ok=True)
    np.save("artifacts/metrics/tfidf_val_probs.npy", val_probs)
    np.save("artifacts/metrics/tfidf_test_probs.npy", test_probs)
    
    # 6. Evaluate on Test set
    y_pred = clf.predict(X_test_vec)
    report = classification_report(y_test, y_pred)
    print("\nTest Set Classification Report:")
    print(report)
    
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary")
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1)
    }
    
    with open("artifacts/metrics/tfidf_eval.json", "w") as f:
        json.dump(metrics, f, indent=4)
        
    print("Saved evaluation metrics to artifacts/metrics/tfidf_eval.json")

if __name__ == "__main__":
    train()

