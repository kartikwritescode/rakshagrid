# Developer Walkthrough - Digital Arrest Scam Detection

This document provides a step-by-step walkthrough for training models, calibrating thresholds, serving the API, and testing endpoints.

---

## Part 1: Model Training Pipeline

We follow a modular pipeline where we train individual classifiers, save their validation/test predictions, train a meta-classifier, and calibrate decision boundaries.

### Step 1: Classical TF-IDF Model
Trains a `TfidfVectorizer` + `LogisticRegression` classifier:
```powershell
$env:PYTHONPATH="."
.venv\Scripts\python training/train_tfidf.py
```
* **Output**: Saves `tfidf_vectorizer.joblib`, `tfidf_logreg.joblib` to `artifacts/`, and predictions to `artifacts/metrics/`.

### Step 2: Transformer Fine-Tuning
Fine-tunes a sequence classification model (`distilbert-base-uncased`) and applies PyTorch dynamic quantization:
```powershell
$env:PYTHONPATH="."
.venv\Scripts\python training/train_transformer.py --model distilbert-base-uncased --max_steps 30 --batch_size 8
```
* **Note**: In a CUDA-enabled GPU environment, you can run training without max_steps limits:
  ```powershell
  .venv\Scripts\python training/train_transformer.py --epochs 3
  ```
* **Output**: Saves standard & quantized weights to `artifacts/scam-transformer/` and predictions to `artifacts/metrics/`.

### Step 3: Stacking Ensemble Training
Trains a `LogisticRegression` meta-classifier on the validation set features (`[tfidf_prob, transformer_prob, rules_score, 9 engineered features]`):
```powershell
$env:PYTHONPATH="."
.venv\Scripts\python training/train_ensemble.py
```
* **Output**: Saves `ensemble_meta.joblib` to `artifacts/` and logs performance metrics comparing ensemble against baselines.

### Step 4: Decision Boundary Calibration
Sweeps validation predictions to define optimal decision thresholds ensuring Precision >= 90%, Recall >= 85%, and FPR < 5%:
```powershell
$env:PYTHONPATH="."
.venv\Scripts\python training/calibrate_thresholds.py
```
* **Output**: Saves calibrated thresholds to `artifacts/calibrated_thresholds.json` and evaluations to `artifacts/metrics/final_eval.json`.

---

## Part 2: Serving the FastAPI Web Server

To run the local web server:
```powershell
.venv\Scripts\uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Once running, verify the status of the models using the health check endpoint:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

---

## Part 3: Manual API Verification

You can verify the classification endpoints via curl or PowerShell `Invoke-RestMethod`.

### 1. Legit Transcript Test
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/scam/analyze-text" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"transcript": "Hi mom, I am heading home now. See you for dinner!"}'
```

### 2. Digital Arrest Scam Test
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/scam/analyze-text" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"transcript": "This is Delhi Police Headquarters. A case of money laundering has been registered under your name. You are under digital arrest. You must transfer funds to the verification account immediately or go to jail."}'
```

### 3. SSE Streaming Test
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/scam/stream" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"transcript_chunks": ["This is police.", "You are under arrest.", "Transfer funds now."]}'
```
*(This returns an event stream showing real-time rules-based risk score updates).*
