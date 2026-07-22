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
├── backend/                  # Centralized FastAPI REST Application
│   └── fastapi/
│       ├── app/
│       │   ├── api/          # Low-level API abstractions
│       │   ├── config/       # Settings & environment variables
│       │   ├── core/         # Lifespan events & startup initializers
│       │   ├── middleware/   # CORS & Centralized Exception Handlers
│       │   ├── routers/      # Audio, Scam, Currency, Crime, Health routers
│       │   ├── schemas/      # Pydantic request/response schemas
│       │   └── services/     # Service layer wrapping ML interfaces
│       ├── Dockerfile
│       └── requirements.txt
├── frontend/                 # Next.js 14 Production Web Interface
│   └── nextjs/
│       ├── src/
│       │   ├── api/          # Generic HTTP client (client.ts)
│       │   ├── components/   # UI components (LeafletCrimeMap, GraphView, RiskScorePanel)
│       │   ├── constants/    # API endpoints & configuration
│       │   ├── hooks/        # React custom hooks (useAudioDetector, useCrimeMap)
│       │   ├── pages/        # 18 Prerendered Static & Dynamic Pages
│       │   ├── services/     # API Service calls to FastAPI backend
│       │   ├── styles/       # Tailwind CSS & global glassmorphism styles
│       │   └── types/        # TypeScript interfaces matching FastAPI schemas
│       └── Dockerfile
├── ml/                       # Standalone Machine Learning Modules
│   ├── module1_currency/     # Counterfeit Banknote Detector (EfficientNetB0)
│   ├── module2/              # Scam Interceptor (Whisper + Stacking Ensemble + Groq LLM)
│   └── module4_crime/        # VigilGrid Crime Engine (Haversine DBSCAN Hotspots)
├── shared/                   # Cross-cutting Shared Utilities
├── storage/                  # Mounted Persistent Storage (models, outputs, uploads)
├── scripts/                  # Cross-Platform Launcher Scripts (dev.bat, dev.sh, build.sh)
└── docker-compose.yml        # Multi-Container Orchestration
```

---

## ✨ Key Features

### 🎵 1. Audio Deepfake & Call Scam Interceptor (Modules 2 & 3)
- Multi-tier speech transcription supporting **`.ogg`, `.wav`, `.mp3`, `.m4a`, `.flac`, `.webm`, `.opus`**.
- Powered by `Faster-Whisper` + `OpenAI Whisper` + `Groq Cloud Audio API`.
- **Bounded Stacking Ensemble** (`scipy L-BFGS-B` non-negative meta-classifier) evaluating TF-IDF, DistilBERT PyTorch transformers, and 9 engineered risk features.
- Groq `Llama-3.3-70b-versatile` LLM fallback for borderline verification.

### 💵 2. Counterfeit Currency Scanner (Module 1)
- Deep vision CNN model (`EfficientNetB0`) analyzing banknote images (224x224).
- Detects counterfeit print defects, color shifts, and missing security thread patterns.

### 🗺️ 3. Interactive Leaflet.js Crime Map & Hotspot Engine (Module 4)
- **VigilGrid Engine**: Haversine `DBSCAN` spatial clustering over latitude/longitude incident point clouds (`eps=0.4km`, `min_samples=20`).
- **Interactive Dark Map**: Uses `CartoDB Dark` map tiles, custom severity markers, popup telemetry, live search, severity filters, and patrol unit allocation.

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

> **Note**: `scripts/dev.bat` automatically frees locked ports (3000 & 8000), configures python paths, and opens separate pop-up windows for the backend and frontend.

---

### 3️⃣ Running Manually Step-by-Step in VS Code Terminals

#### Terminal 1 — FastAPI Central Backend (Port 8000)
```powershell
# 1. Ensure you are in project root
cd C:\files\programming\Python\projects\rakshagrid

# 2. Install backend dependencies
pip install -r backend/fastapi/requirements.txt

# 3. Start FastAPI server
python -m uvicorn backend.fastapi.app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend runs at: **[http://localhost:8000](http://localhost:8000)** (Interactive Docs: **[http://localhost:8000/docs](http://localhost:8000/docs)**)*

#### Terminal 2 — Next.js Frontend (Port 3000)
```powershell
# 1. Navigate to frontend directory
cd frontend/nextjs

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

| Endpoint Path | Method | Module | Description |
| :--- | :--- | :--- | :--- |
| `/health` | `GET` | System | Central runtime health check across all ML modules |
| `/api/currency/predict` | `POST` | Module 1 | Counterfeit banknote image defect scan |
| `/api/audio/detect` | `POST` | Module 2 | Audio recording (.ogg/mp3/wav) deepfake & scam interceptor |
| `/api/audio/transcribe` | `POST` | Module 3 | Whisper speech-to-text audio transcription |
| `/api/scam/analyze-text` | `POST` | Module 2 | Text transcript scam risk classification |
| `/api/crime/predict` | `POST` | Module 4 | Crime scene image/video evidence analysis |
| `/api/crime/incidents` | `GET` | Module 4 | Incident point cloud formatted for Leaflet.js markers |
| `/api/crime/hotspots` | `GET` | Module 4 | DBSCAN crime hotspot clusters |
| `/api/crime/patrol-allocation` | `GET` | Module 4 | Patrol resource allocation engine |

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

## 🧪 Production Verification

To verify that all Next.js pages and FastAPI backend routes compile cleanly:

```bash
# 1. Verify Backend & ML Modules
python -c "from backend.fastapi.app.main import app; print('✓ Backend OK')"

# 2. Verify Frontend Production Build
cd frontend/nextjs && npm run build
```

---

<div align="center">

Made with ❤️ by the **Raksha Grid Engineering Team**

</div>
