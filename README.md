# Raksha Grid - Digital Arrest Scam Detection Service (Module 1)

Raksha Grid is a real-time call and text interceptor designed to detect and block digital arrest scams. This repository contains the complete implementation and test suite for **Module 1: Digital Arrest Scam Detection & Alerting**.

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
4. **Layer D: Transformer Layer**: Light-weight, CPU-quantized DistilBERT model with optimized inference latency.
5. **Layer E: Stacking Ensemble**: Combines the predictions from Layers A-D using a Logistic Regression meta-classifier.
6. **Layer F: LLM Fallback (Groq)**: Borderline cases are sent to Llama-3.3-70b via Groq to obtain a final expert opinion.

## API Endpoints

- **`GET /health`**: Returns system and model loading status.
- **`POST /api/scam/analyze-text`**: Processes a text transcript through the full stacked ensemble and returns an explainable verdict.
- **`POST /api/scam/analyze-audio`**: Transcribes audio files via Whisper and pipes the transcript to the text classification pipeline.
- **`POST /api/scam/stream`**: Returns an SSE stream of risk updates as the conversation progresses.

## Quick Start

### Installation

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest httpx
   ```
3. Set up your environment variables in `.env`:
   ```env
   GROQ_API_KEY=your_free_groq_api_key
   ```

### Running the Service

Start the FastAPI serving app:
```bash
.venv\Scripts\uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The API documentation is available at `http://localhost:8000/docs`.

### Testing

Run the unit and integration tests:
```bash
$env:PYTHONPATH="."; .venv\Scripts\python -m pytest
```
