<div align="center">

# 🛡️ RAKSHA GRID — UNIFIED AI SAFETY & CRIME INTELLIGENCE PLATFORM

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.3-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.11-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Leaflet.js](https://img.shields.io/badge/Leaflet-1.9.4-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

*An Enterprise Multi-Tier AI Platform for Digital Arrest Scam Interception, Audio Deepfake Voice Biometrics, Counterfeit Currency Scanning, and Geospatial Crime Intelligence.*

[🚀 Quick Start](#-quick-start--local-walkthrough) • [✨ Key Features](#-key-features) • [📡 API Documentation](#-api-endpoints) • [🏗️ Architecture](#%EF%B8%8F-monorepo-architecture) • [🧪 Verification](#-verification--testing)

</div>

---

## 🏗️ Monorepo Architecture Layout

```text
rakshagrid/
├── apps/
│   ├── api/                      # Centralized FastAPI REST Application
│   │   ├── src/
│   │   │   ├── main.py           # Unified entrypoint mounting /api & /api/v1
│   │   │   ├── config.py         # App configuration & settings
│   │   │   ├── core/             # Lifespan events & startup initializers
│   │   │   ├── middleware/       # CORS & Centralized Exception Handlers
│   │   │   ├── routers/v1/       # Audio, Scam, Currency, Crime, Health routers
│   │   │   ├── services/         # Service layer wrapping ML packages
│   │   │   └── schemas/          # Pydantic request/response schemas
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── web/                      # Next.js 14 Production Web Interface
│       ├── src/
│       │   ├── components/       # UI components (LeafletCrimeMap, GraphView, RiskScorePanel)
│       │   ├── pages/            # Next.js Pages & Views
│       │   ├── services/         # API Service calls to FastAPI backend
│       │   └── styles/           # Tailwind CSS & global styles
│       ├── public/
│       ├── package.json
│       └── Dockerfile
│
├── packages/                     # Clean Namespaced Python Packages (`rakshagrid.*`)
│   ├── ai-scam/                  # Call Scam Interceptor & Whisper Audio Biometrics
│   ├── ai-currency/              # Counterfeit Banknote Vision Classifier
│   ├── ai-crime/                 # VigilGrid Geospatial DBSCAN Hotspot Engine
│   ├── ai-graph/                 # Graph Intelligence & Crime Network Builder
│   └── common/                   # Cross-cutting configs, logging, exceptions, utils
│
├── pipelines/                    # ML Training & Evaluation Pipelines
│   ├── training/                 # Ensemble, TF-IDF, Transformer training scripts
│   ├── evaluation/               # Adversarial & calibration benchmarks
│   └── notebooks/                # Exploratory notebooks
│
├── data/                         # Datasets & Sources
│   ├── raw/                      # Ground truth raw datasets & sources
│   ├── processed/                # Processed point clouds & training data
│   └── README.md
│
├── storage/                      # Persistent Runtime Assets
│   ├── models/                   # Serialized model weights & caches
│   ├── uploads/                  # Temporary file upload staging
│   └── outputs/                  # Exported outputs & clusters
│
├── tests/
│   ├── integration/              # API and rule integration tests
│   └── e2e/                      # End-to-end test scenarios
│
├── scripts/                      # Cross-Platform Launcher Scripts (dev.bat, dev.sh)
├── docs/                         # Architecture & Migration Documentation
├── docker-compose.yml            # Multi-Container Orchestration
├── .dockerignore
├── .gitignore
└── pyproject.toml                # Root packaging & Pytest configuration
```

---

## ✨ Key Features

### 🎵 1. Audio Deepfake & Call Scam Interceptor (`rakshagrid.ai_scam`)
- Multi-tier speech transcription supporting **`.ogg`, `.wav`, `.mp3`, `.m4a`, `.flac`, `.webm`, `.opus`**.
- Powered by `Faster-Whisper` + `OpenAI Whisper` + `Groq Cloud Audio API`.
- **Bounded Stacking Ensemble** (`scipy L-BFGS-B` non-negative meta-classifier) evaluating TF-IDF, DistilBERT PyTorch transformers, and 9 engineered risk features.
- Groq `Llama-3.3-70b-versatile` LLM fallback for borderline verification.

### 💵 2. Counterfeit Currency Scanner (`rakshagrid.ai_currency`)
- Deep vision CNN model (`EfficientNetB0`) analyzing banknote images (224x224).
- Detects counterfeit print defects, color shifts, and missing security thread patterns.

### 🗺️ 3. Interactive Leaflet.js Crime Map & Hotspot Engine (`rakshagrid.ai_crime`)
- **VigilGrid Engine**: Haversine `DBSCAN` spatial clustering over latitude/longitude incident point clouds (`eps=0.4km`, `min_samples=20`).
- **Interactive Dark Map**: Uses `CartoDB Dark` map tiles, custom severity markers, popup telemetry, live search, severity filters, and patrol unit allocation.

### 🕸️ 4. Graph Network Intelligence (`rakshagrid.ai_graph`)
- Graph analysis engine with network centrality, syndicate ring detection, and transaction flow visualization.

---

## 🚀 Quick Start & Local Walkthrough

### 1️⃣ Prerequisites & Environment Setup

Copy `.env.example` to `.env` in the root directory:
```bash
cp .env.example .env
```

Ensure your `.env` contains:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama-3.3-70b-versatile
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 2️⃣ Running via Automated Script (Recommended)

From the project root directory (`rakshagrid/`):

#### 🪟 Windows (PowerShell / Command Prompt)
```cmd
.\scripts\dev.bat
```

#### 🐧 Linux / macOS / Git Bash
```bash
chmod +x ./scripts/dev.sh
./scripts/dev.sh
```

> **Note**: `scripts/dev.bat` automatically frees locked ports (3000 & 8000), configures python paths, and launches the backend and frontend.

---

### 3️⃣ Running Manually Step-by-Step in VS Code Terminals

#### Terminal 1 — FastAPI Central Backend (Port 8000)
```powershell
# 1. Ensure you are in project root
cd C:\files\programming\Python\projects\rakshagrid

# 2. Install dependencies & packages in editable mode
pip install -r apps/api/requirements.txt
pip install -e packages/common -e packages/ai-scam -e packages/ai-currency -e packages/ai-crime -e packages/ai-graph -e apps/api

# 3. Start FastAPI server
python -m uvicorn rakshagrid.api.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend runs at: **[http://localhost:8000](http://localhost:8000)** (Interactive Docs: **[http://localhost:8000/docs](http://localhost:8000/docs)**)*

#### Terminal 2 — Next.js Frontend (Port 3000)
```powershell
# 1. Navigate to frontend directory
cd apps/web

# 2. Install Node packages
npm install

# 3. Start Next.js dev server
npm run dev
```
*Frontend runs at: **[http://localhost:3000](http://localhost:3000)**.*

---

### 🐳 4️⃣ Running via Docker Compose

```bash
docker-compose up --build
```

---

## 📡 API Endpoints & Testing Snippets

Both `/api/...` and `/api/v1/...` routes are mounted for full backwards compatibility.

| Endpoint Path | Method | Module | Description |
| :--- | :--- | :--- | :--- |
| `/health` | `GET` | System | Central runtime health check across all ML modules |
| `/api/currency/predict` | `POST` | `ai-currency` | Counterfeit banknote image defect scan |
| `/api/audio/detect` | `POST` | `ai-scam` | Audio recording (.ogg/mp3/wav) deepfake & scam interceptor |
| `/api/audio/transcribe` | `POST` | `ai-scam` | Whisper speech-to-text audio transcription |
| `/api/scam/analyze-text` | `POST` | `ai-scam` | Text transcript scam risk classification |
| `/api/crime/predict` | `POST` | `ai-crime` | Crime scene image/video evidence analysis |
| `/api/crime/incidents` | `GET` | `ai-crime` | Incident point cloud formatted for Leaflet.js markers |
| `/api/crime/hotspots` | `GET` | `ai-crime` | DBSCAN crime hotspot clusters |
| `/api/crime/patrol-allocation` | `GET` | `ai-crime` | Patrol resource allocation engine |

### 🧪 Example cURL Requests

#### 1. Test Scam Interceptor Text Analysis:
```bash
curl -X POST "http://localhost:8000/api/scam/analyze-text" \
     -H "Content-Type: application/json" \
     -d '{"transcript": "This is Officer Sharma from CBI. Your bank account is locked under digital arrest. Transfer 50000 rupees immediately."}'
```

#### 2. Test Audio Deepfake & STT (.ogg / .wav / .mp3):
```bash
curl -X POST "http://localhost:8000/api/audio/detect" \
     -F "file=@sample_call.ogg"
```

---

## 🧪 Production Verification & Testing

To verify the monorepo test suite and import integrity:

```bash
# 1. Run Python import checks across all packages
python -c "from rakshagrid.common.configs.base_config import BASE_DIR; from rakshagrid.ai_scam import predict; from rakshagrid.ai_currency import predict; from rakshagrid.ai_crime import predict_hotspots; from rakshagrid.ai_graph import build_graph_from_reports; from apps.api.src.main import app; print('✓ All package namespaces verified')"

# 2. Run Pytest Integration Suite
python -m pytest tests/

# 3. Verify Frontend Production Build (optional)
cd apps/web && npm run build
```

---

<div align="center">

Made with ❤️ by the **Raksha Grid Engineering Team**

</div>
