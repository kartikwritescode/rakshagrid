# Raksha Grid - Digital Arrest Scam Detection Service (Module 1)

Raksha Grid is a real-time call and text interceptor designed to detect and block digital arrest scams. This repository contains the complete implementation and test suite for **Module 1: Digital Arrest Scam Detection & Alerting**.

---

## Architecture Overview

The detection service utilizes a multi-layer ensemble architecture running in the following order:

```
                  +-----------------------------------+
                  |        Incoming Transcript        |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Layer A: Rules Scorer (Lexicon)  |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Layer B: Engineered Features     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Layer C: TF-IDF + Logistic Reg.  |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Layer D: Fine-tuned DistilBERT   |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Layer E: Stacking Meta-Classifier|
                  +-----------------------------------+
                                    |
            +-----------------------+-----------------------+
            | Confident Verdict                             | Needs Review (Borderline)
            v                                               v
+-----------------------+                       +-----------------------+
|  Return high/low Band |                       | Layer F: LLM Fallback |
+-----------------------+                       +-----------------------+
                                                            |
                                                +-----------+-----------+
                                                | Confident | Uncertain |
                                                v           v           v
                                            Adopt LLM   Keep needs_review
```

1. **Layer A: Rules/Lexicon Layer**: Fast keyword matching providing instant feedback and fired features.
2. **Layer B: Feature Engineering**: Extracts 9 lexical features matching training distributions exactly.
3. **Layer C: TF-IDF Layer**: Solo classical machine learning model.
4. **Layer D: Transformer Layer**: Fine-tuned DistilBERT model.
5. **Layer E: Stacking Ensemble**: Combines predictions from Layers A-D using a Logistic Regression meta-classifier.
6. **Layer F: LLM Fallback (Groq)**: Borderline cases are sent to Llama-3.3-70b via Groq to obtain a final expert opinion.

---

## Final Pass Changelog

This final pass focused on repository cleanup, targeted accuracy fixes, and documentation:

1. **Repository Cleanup**:
   * Removed `training/prepare_dataset.py` (superseded by `training/augment_dataset.py`).
   * Removed `artifacts/scam-distilbert` (empty directory).
2. **Rules Safety Override**:
   * Implemented a post-processing safety rule: if the rules score is high (`rules_score >= 0.40`) but the ensemble predicts `"low"`, the verdict is overridden to `"needs_review"` and routed to the LLM fallback to prevent false negatives.
3. **Institutional False Positives Fix**:
   * Augmented splits with **30 new custom benign examples** (15 bank alerts and 15 verification notifications) written to mimic formal/IVR structures ("press 1 to confirm", "no action needed if valid", etc.) without asking for personal credentials.
   * Retrained all models (TF-IDF, DistilBERT, Ensemble) and recalibrated decision thresholds to **Low = 0.3600** and **High = 0.7100**.

---

## Quick Start (Clean Clone Setup)

### 1. Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows PowerShell

# Install required dependencies
pip install -r requirements.txt
```

### 2. `.env` Configuration
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_free_tier_groq_api_key
```

### 3. Model Training
You can run the models using the committed pre-trained artifacts directly, or reproduce training from scratch:
```powershell
$env:PYTHONPATH="."

# 1. Inject benign hard negatives and scams
python training/augment_dataset.py

# 2. Retrain TF-IDF model
python training/train_tfidf.py

# 3. Retrain DistilBERT model (requires CUDA recommended)
python training/train_transformer.py --epochs 5 --batch_size 16

# 4. Train Stacking Ensemble meta-classifier
python training/train_ensemble.py

# 5. Calibrate risk thresholds
python training/calibrate_thresholds.py
```

### 4. Start the Service
```powershell
.venv\Scripts\uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Access the interactive documentation at `http://localhost:8000/docs`.

---

## Testing & Evaluation

### Run Test Suite
```powershell
$env:PYTHONPATH="."
python -m pytest
```

### Run Adversarial Evaluation
```powershell
$env:PYTHONPATH="."
python training/eval_adversarial.py
```

---

## API Usage Examples

### 1. Health Status
**Request**:
```bash
curl http://localhost:8000/health
```
**Response**:
```json
{
  "status": "healthy",
  "models_status": {
    "tfidf": "loaded",
    "transformer": "loaded",
    "ensemble": "loaded",
    "rules": "ready"
  }
}
```

### 2. Analyze Call Transcript
**Request**:
```bash
curl -X POST -H "Content-Type: application/json" -d "{\"transcript\": \"hello this is alex from microsoft\"}" http://localhost:8000/api/scam/analyze-text
```
**Response**:
```json
{
  "stage": "llm_fallback",
  "risk_score": 0.0,
  "risk_band": "low",
  "fired_features": [],
  "fired_features_detail": [],
  "component_scores": {
    "rules": 0.0,
    "tfidf": 0.3541,
    "transformer": 0.0388,
    "ensemble": 0.1288,
    "llm_fallback": 0.0
  },
  "breakdown": {
    "engineered_features": {
      "turn_count": 0,
      "char_len": 32,
      "word_count": 6,
      "placeholder_count": 0,
      "urgency_word_count": 0,
      "money_word_count": 0,
      "authority_word_count": 0,
      "has_phone_number": 0,
      "exclaim_count": 0
    },
    "rules_detail": []
  },
  "transcript": "hello this is alex from microsoft"
}
```

---

## Final Performance Scoreboard

These metrics are reported strictly on the handwritten, placeholders-free adversarial dataset (`data/adversarial_eval.csv`):

| Evaluation Dataset | Decisive Accuracy | Precision | Recall | False Positive Rate | Needs Review Rate |
|---|---|---|---|---|---|
| **Old Adversarial Set (Baseline)** | 93.44% | 88.89% | 96.00% | 8.33% | 1.61% |
| **New Rebuilt Adversarial Set** | **96.72%** | **96.00%** | **96.00%** | **2.78%** | **1.61%** |
| **HuggingFace Test Split (`test.csv`)*** | 99.32% | 99.33% | 94.30% | 0.68% | 3.95% |

*\*Note: HuggingFace splits contain synthetic templates and are included for baseline reference only. The adversarial eval is the trusted evaluation set.*

### Format Robustness Breakdown:
* **Single-Turn Format**: **`94.12%`** Decisive Accuracy | **`5.00%`** FPR
* **Multi-Turn `caller:/receiver:` Format**: **`100.00%`** Decisive Accuracy | **`0.00%`** FPR

#### Cross-Format performance gap:
The single-message/SMS style remains slightly more challenging than the dialogue format, but the new benign data closed the single-turn false positive rate from **`10.53%`** to **`5.00%`**, demonstrating strong format-invariant generalization.
